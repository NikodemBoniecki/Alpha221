import argparse
import csv
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np

from .bootstrap import positive_return_probabilities, sample_block_bootstrap
from .backtest import run_walk_forward
from .data import calculate_returns, load_prices, make_demo_prices
from .exhaustive import exhaustive_subset_markowitz
from .genetic import GeneticConfig, optimize_genetic
from .portfolio import PortfolioResult, equal_weight_portfolio, markowitz_portfolio
from .universe import ASSETS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare portfolio optimization methods.")
    parser.add_argument("--input", type=Path, help="CSV with a date column and one price column per ticker.")
    parser.add_argument("--risk-limit", type=float, default=0.25, help="Maximum annualized volatility, for example 0.25.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for the genetic algorithm.")
    parser.add_argument("--population", type=int, default=100, help="Number of portfolios in the GA population.")
    parser.add_argument("--generations", type=int, default=200, help="Maximum number of GA generations.")
    parser.add_argument("--yearly", action="store_true", help="Evaluate each calendar year separately.")
    parser.add_argument(
        "--walk-forward",
        action="store_true",
        help="Run the two-year/ five-year weekly out-of-sample evaluation.",
    )
    parser.add_argument(
        "--exhaustive-subsets",
        action="store_true",
        help="Evaluate all 3,003 10-stock subsets with Markowitz weights (weekly input only).",
    )
    parser.add_argument(
        "--frequency",
        choices=("daily", "weekly"),
        default="daily",
        help="Sampling frequency of the input prices; annualizes with 252 or 52 periods.",
    )
    parser.add_argument(
        "--probability-simulations",
        type=int,
        default=10_000,
        help="Bootstrap paths used for reported six-month probabilities (default: 10000).",
    )
    parser.add_argument(
        "--optimization-simulations",
        type=int,
        default=1_000,
        help="Bootstrap paths per GA fitness evaluation (default: 1000).",
    )
    parser.add_argument("--output", type=Path, default=Path("results/comparison.csv"), help="Where to save the comparison CSV.")
    parser.add_argument(
        "--fold-output",
        type=Path,
        default=Path("results/walk_forward_folds.csv"),
        help="Walk-forward fold results CSV.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/walk_forward_summary.csv"),
        help="Walk-forward summary CSV.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.risk_limit <= 0:
        parser.error("--risk-limit must be greater than zero.")
    if args.population < 10 or args.generations < 1:
        parser.error("--population must be at least 10 and --generations must be positive.")
    if args.probability_simulations < 1 or args.optimization_simulations < 1:
        parser.error("Bootstrap simulation counts must be positive.")
    if args.walk_forward and (args.yearly or args.frequency != "weekly" or not args.input):
        parser.error("--walk-forward requires a weekly input file and cannot be combined with --yearly.")
    if args.exhaustive_subsets and (
        args.walk_forward or args.yearly or args.frequency != "weekly" or not args.input
    ):
        parser.error(
            "--exhaustive-subsets requires a weekly input file and cannot be combined with "
            "--yearly or --walk-forward."
        )

    try:
        periods_per_year = 252 if args.frequency == "daily" else 52
        if args.input:
            tickers, dates, prices = load_prices(args.input)
            print(f"Loaded prices from {args.input}.")
        else:
            tickers, dates, prices = make_demo_prices()
            print(f"Using built-in synthetic prices for {len(tickers)} tickers and {len(dates)} dates.")

        _validate_frequency(dates, args.frequency)

        config = GeneticConfig(population_size=args.population, generations=args.generations)
        if args.walk_forward:
            folds, summary = run_walk_forward(
                tickers,
                dates,
                prices,
                args.risk_limit,
                args.seed,
                config,
                args.probability_simulations,
                args.optimization_simulations,
            )
            _write_rows(args.fold_output, folds)
            _write_rows(args.summary_output, summary)
            print("Five-year walk-forward summary:")
            for row in summary:
                print(
                    f"{row['method']:<24} return={row['five_year_compounded_return']:.2%} "
                    f"positive periods={row['positive_period_rate']:.1%} "
                    f"realized volatility={row['realized_annualized_volatility']:.2%}"
                )
            print(f"Saved fold results to {args.fold_output}.")
            print(f"Saved summary to {args.summary_output}.")
            return
        if args.yearly:
            records = _evaluate_years(
                dates,
                prices,
                args.risk_limit,
                args.seed,
                config,
                periods_per_year,
                args.probability_simulations,
                args.optimization_simulations,
                tickers,
            )
        else:
            records = [
                (
                    "all",
                    _compare_methods(
                        prices,
                        args.risk_limit,
                        args.seed,
                        config,
                        periods_per_year,
                        args.probability_simulations,
                        args.optimization_simulations,
                        tickers,
                        args.exhaustive_subsets,
                    ),
                )
            ]

        _print_results(records, tickers, args.risk_limit, args.frequency, periods_per_year)
        if args.yearly:
            _print_yearly_summary(records)
        _save_results(
            records,
            tickers,
            args.risk_limit,
            args.frequency,
            periods_per_year,
            args.probability_simulations,
            args.optimization_simulations,
            args.output,
        )
        print(f"Saved comparison to {args.output}.")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to save to {path}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _validate_frequency(dates: list[date], frequency: str) -> None:
    gaps = np.array([(current - previous).days for previous, current in zip(dates, dates[1:])])
    if not len(gaps):
        raise ValueError("At least two dates are required to identify the input frequency.")

    median_gap = float(np.median(gaps))
    if frequency == "weekly" and not np.all(gaps == 7):
        raise ValueError(
            "Weekly input must use consecutive Friday-ending weekly rows; "
            "use data/prices_weekly_usd.csv from the market-data command."
        )
    if frequency == "daily" and median_gap > 4:
        raise ValueError(
            "The input dates look weekly, but --frequency daily is selected. "
            "Pass --frequency weekly to annualize with 52 periods."
        )


def _evaluate_years(
    dates: list[date],
    prices: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig,
    periods_per_year: int,
    probability_simulations: int,
    optimization_simulations: int,
    tickers: list[str],
) -> list[tuple[str, list[PortfolioResult]]]:
    records = []
    years = sorted({item.year for item in dates})

    for year in years:
        indices = [index for index, item in enumerate(dates) if item.year == year]
        if len(indices) < 3:
            continue
        yearly_prices = prices[indices]
        yearly_seed = seed + year
        results = _compare_methods(
            yearly_prices,
            risk_limit,
            yearly_seed,
            config,
            periods_per_year,
            probability_simulations,
            optimization_simulations,
            tickers,
        )
        records.append((str(year), results))

    if not records:
        raise ValueError("There are no calendar years with at least three price rows.")
    return records


def _compare_methods(
    prices: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig,
    periods_per_year: int,
    probability_simulations: int = 10_000,
    optimization_simulations: int = 1_000,
    tickers: list[str] | None = None,
    include_exhaustive_subsets: bool = False,
) -> list[PortfolioResult]:
    returns = calculate_returns(prices)
    mean_returns = np.mean(returns, axis=0)
    covariance = np.cov(returns, rowvar=False, ddof=1)
    if np.ndim(covariance) == 0:
        covariance = np.array([[float(covariance)]])

    optimization_scenarios = None
    if periods_per_year == 52:
        optimization_scenarios = sample_block_bootstrap(
            returns,
            horizon_weeks=26,
            block_length=4,
            simulations=optimization_simulations,
            seed=seed,
        )
    target_universe = tickers == ASSETS
    report_scenarios: dict[int, np.ndarray] = {}

    genetic = optimize_genetic(
        mean_returns,
        covariance,
        risk_limit,
        seed,
        config,
        periods_per_year,
        optimization_scenarios,
        enforce_project_constraints=target_universe,
    )
    markowitz = markowitz_portfolio(
        mean_returns,
        covariance,
        risk_limit,
        periods_per_year,
        stock_count=15 if target_universe else None,
    )
    equal_weight = equal_weight_portfolio(
        mean_returns,
        covariance,
        risk_limit,
        periods_per_year,
        stock_count=15 if target_universe else None,
    )
    results = [genetic, markowitz, equal_weight]
    if include_exhaustive_subsets:
        if target_universe is not True or optimization_scenarios is None:
            raise ValueError("Exhaustive subset search requires the project's weekly asset universe.")
        report_scenarios[4] = sample_block_bootstrap(
            returns,
            horizon_weeks=26,
            block_length=4,
            simulations=probability_simulations,
            seed=seed + 10_004,
        )
        results.append(
            exhaustive_subset_markowitz(
                mean_returns,
                covariance,
                risk_limit,
                periods_per_year,
                report_scenarios[4],
                progress=lambda done, total: print(
                    f"Evaluated {done:,}/{total:,} candidate subsets.", flush=True
                ),
            )
        )
    if periods_per_year == 52:
        sensitivities: dict[int, np.ndarray] = {}
        for block_length in (2, 4, 8):
            scenarios = report_scenarios.get(block_length)
            if scenarios is None:
                scenarios = sample_block_bootstrap(
                    returns,
                    horizon_weeks=26,
                    block_length=block_length,
                    simulations=probability_simulations,
                    seed=seed + 10_000 + block_length,
                )
                report_scenarios[block_length] = scenarios
            sensitivities[block_length] = np.array(
                [
                    positive_return_probabilities(result.weights, scenarios)[0]
                    for result in results
                ]
            )
        results = [
            replace(
                result,
                probability_positive_6m=float(sensitivities[4][index]),
                probability_sensitivity={
                    2: float(sensitivities[2][index]),
                    8: float(sensitivities[8][index]),
                },
            )
            for index, result in enumerate(results)
        ]
    return results


def _print_results(
    records: list[tuple[str, list[PortfolioResult]]],
    tickers: list[str],
    risk_limit: float,
    frequency: str,
    periods_per_year: int,
) -> None:
    print(f"Risk limit: {risk_limit:.2%} annualized volatility")
    print(f"Input frequency: {frequency} ({periods_per_year} periods per year)")
    for period, results in records:
        print(f"\nPeriod: {period}")
        print(
            f"{'Method':<24} {'Return':>10} {'Risk':>10} "
            f"{'P(+6m)':>10} {'P2w/P8w':>16} {'Within limit':>15}"
        )
        for result in results:
            probability = (
                f"{result.probability_positive_6m:.2%}"
                if result.probability_positive_6m is not None
                else "n/a"
            )
            sensitivity = (
                f"{result.probability_sensitivity[2]:.1%}/"
                f"{result.probability_sensitivity[8]:.1%}"
                if result.probability_sensitivity is not None
                else "n/a"
            )
            print(
                f"{result.method:<24} {result.annual_return:>9.2%} "
                f"{result.annual_volatility:>9.2%} {probability:>10} "
                f"{sensitivity:>16} {str(result.feasible):>15}"
            )
            weights = ", ".join(
                f"{ticker}={weight:.1%}" for ticker, weight in zip(tickers, result.weights)
            )
            print(f"  Weights: {weights}")
            if result.candidate_subsets is not None:
                print(
                    f"  Subsets: {result.candidate_subsets:,} evaluated, "
                    f"{result.feasible_candidate_subsets:,} risk-feasible."
                )


def _save_results(
    records: list[tuple[str, list[PortfolioResult]]],
    tickers: list[str],
    risk_limit: float,
    frequency: str,
    periods_per_year: int,
    probability_simulations: int,
    optimization_simulations: int,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "period",
                "frequency",
                "periods_per_year",
                "method",
                "annual_return",
                "annual_volatility",
                "probability_positive_6m",
                "probability_block2",
                "probability_block8",
                "candidate_subsets",
                "feasible_candidate_subsets",
                "probability_horizon_weeks",
                "probability_primary_block_weeks",
                "probability_simulations",
                "optimization_simulations",
                "risk_limit",
                "feasible",
                "return_ratio_to_markowitz",
                "weights",
            ],
        )
        writer.writeheader()
        for period, results in records:
            markowitz_return = next(result.annual_return for result in results if result.method == "Markowitz")
            for result in results:
                writer.writerow(
                    {
                        "period": period,
                        "frequency": frequency,
                        "periods_per_year": periods_per_year,
                        "method": result.method,
                        "annual_return": result.annual_return,
                        "annual_volatility": result.annual_volatility,
                        "probability_positive_6m": result.probability_positive_6m,
                        "probability_block2": (
                            result.probability_sensitivity[2]
                            if result.probability_sensitivity is not None
                            else ""
                        ),
                        "probability_block8": (
                            result.probability_sensitivity[8]
                            if result.probability_sensitivity is not None
                            else ""
                        ),
                        "candidate_subsets": result.candidate_subsets or "",
                        "feasible_candidate_subsets": result.feasible_candidate_subsets or "",
                        "probability_horizon_weeks": (
                            26 if result.probability_positive_6m is not None else ""
                        ),
                        "probability_primary_block_weeks": (
                            4 if result.probability_positive_6m is not None else ""
                        ),
                        "probability_simulations": (
                            probability_simulations
                            if result.probability_positive_6m is not None
                            else ""
                        ),
                        "optimization_simulations": (
                            optimization_simulations
                            if result.probability_positive_6m is not None
                            else ""
                        ),
                        "risk_limit": risk_limit,
                        "feasible": result.feasible,
                        "return_ratio_to_markowitz": (
                            result.annual_return / markowitz_return if markowitz_return > 0 else ""
                        ),
                        "weights": json.dumps(dict(zip(tickers, result.weights.tolist())), ensure_ascii=False),
                    }
                )


def _print_yearly_summary(records: list[tuple[str, list[PortfolioResult]]]) -> None:
    ratios = []
    for _, results in records:
        genetic = next(result for result in results if result.method == "Genetic algorithm")
        markowitz = next(result for result in results if result.method == "Markowitz")
        if markowitz.annual_return > 0:
            ratios.append(genetic.annual_return / markowitz.annual_return)

    if len(ratios) != len(records):
        print("\nMedian GA/Markowitz return ratio is unavailable because at least one Markowitz return is not positive.")
        return

    median_ratio = float(np.median(ratios))
    print(
        f"\nMedian GA/Markowitz return ratio across {len(records)} annual cases: "
        f"{median_ratio:.2%}."
    )
