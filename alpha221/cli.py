import argparse
import csv
import json
from datetime import date
from pathlib import Path

import numpy as np

from .data import calculate_returns, load_prices, make_demo_prices
from .genetic import GeneticConfig, optimize_genetic
from .portfolio import PortfolioResult, equal_weight_portfolio, markowitz_portfolio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare portfolio optimization methods.")
    parser.add_argument("--input", type=Path, help="CSV with a date column and one price column per ticker.")
    parser.add_argument("--risk-limit", type=float, default=0.25, help="Maximum annualized volatility, for example 0.25.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for the genetic algorithm.")
    parser.add_argument("--population", type=int, default=100, help="Number of portfolios in the GA population.")
    parser.add_argument("--generations", type=int, default=200, help="Maximum number of GA generations.")
    parser.add_argument("--yearly", action="store_true", help="Evaluate each calendar year separately.")
    parser.add_argument("--output", type=Path, default=Path("results/comparison.csv"), help="Where to save the comparison CSV.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.risk_limit <= 0:
        parser.error("--risk-limit must be greater than zero.")
    if args.population < 10 or args.generations < 1:
        parser.error("--population must be at least 10 and --generations must be positive.")

    try:
        if args.input:
            tickers, dates, prices = load_prices(args.input)
            print(f"Loaded prices from {args.input}.")
        else:
            tickers, dates, prices = make_demo_prices()
            print(f"Using built-in synthetic prices for {len(tickers)} tickers and {len(dates)} dates.")

        config = GeneticConfig(population_size=args.population, generations=args.generations)
        if args.yearly:
            records = _evaluate_years(dates, prices, args.risk_limit, args.seed, config)
        else:
            records = [("all", _compare_methods(prices, args.risk_limit, args.seed, config))]

        _print_results(records, tickers, args.risk_limit)
        if args.yearly:
            _print_yearly_summary(records)
        _save_results(records, tickers, args.risk_limit, args.output)
        print(f"Saved comparison to {args.output}.")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")


def _evaluate_years(
    dates: list[date],
    prices: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig,
) -> list[tuple[str, list[PortfolioResult]]]:
    records = []
    years = sorted({item.year for item in dates})

    for year in years:
        indices = [index for index, item in enumerate(dates) if item.year == year]
        if len(indices) < 3:
            continue
        yearly_prices = prices[indices]
        yearly_seed = seed + year
        results = _compare_methods(yearly_prices, risk_limit, yearly_seed, config)
        records.append((str(year), results))

    if not records:
        raise ValueError("There are no calendar years with at least three price rows.")
    return records


def _compare_methods(
    prices: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig,
) -> list[PortfolioResult]:
    returns = calculate_returns(prices)
    mean_returns = np.mean(returns, axis=0)
    covariance = np.cov(returns, rowvar=False, ddof=1)
    if np.ndim(covariance) == 0:
        covariance = np.array([[float(covariance)]])

    genetic = optimize_genetic(mean_returns, covariance, risk_limit, seed, config)
    markowitz = markowitz_portfolio(mean_returns, covariance, risk_limit)
    equal_weight = equal_weight_portfolio(mean_returns, covariance, risk_limit)
    return [genetic, markowitz, equal_weight]


def _print_results(records: list[tuple[str, list[PortfolioResult]]], tickers: list[str], risk_limit: float) -> None:
    print(f"Risk limit: {risk_limit:.2%} annualized volatility")
    for period, results in records:
        print(f"\nPeriod: {period}")
        print(f"{'Method':<24} {'Return':>10} {'Risk':>10} {'Within limit':>15}")
        for result in results:
            print(
                f"{result.method:<24} {result.annual_return:>9.2%} "
                f"{result.annual_volatility:>9.2%} {str(result.feasible):>15}"
            )
            weights = ", ".join(
                f"{ticker}={weight:.1%}" for ticker, weight in zip(tickers, result.weights)
            )
            print(f"  Weights: {weights}")


def _save_results(
    records: list[tuple[str, list[PortfolioResult]]],
    tickers: list[str],
    risk_limit: float,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "period",
                "method",
                "annual_return",
                "annual_volatility",
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
                        "method": result.method,
                        "annual_return": result.annual_return,
                        "annual_volatility": result.annual_volatility,
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
    if len(records) != 5:
        print(f"\nMedian GA/Markowitz return ratio for {len(records)} annual cases: {median_ratio:.2%}.")
        print("The project target needs five annual cases, so it cannot be evaluated yet.")
        return

    status = "met" if median_ratio >= 0.95 else "not met"
    print(f"\nMedian GA/Markowitz return ratio: {median_ratio:.2%} (95% target {status}).")
