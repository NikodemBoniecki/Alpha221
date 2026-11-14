import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .data import calculate_returns, load_prices, make_demo_prices
from .genetic import GeneticConfig, optimize_genetic
from .portfolio import equal_weight_portfolio, markowitz_portfolio, portfolio_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare portfolio optimization methods.")
    parser.add_argument("--input", type=Path, help="CSV with a date column and one price column per ticker.")
    parser.add_argument("--risk-limit", type=float, default=0.25, help="Maximum annualized volatility, for example 0.25.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for the genetic algorithm.")
    parser.add_argument("--population", type=int, default=100, help="Number of portfolios in the GA population.")
    parser.add_argument("--generations", type=int, default=200, help="Maximum number of GA generations.")
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
            tickers, prices = load_prices(args.input)
            print(f"Loaded prices from {args.input}.")
        else:
            tickers, dates, prices = make_demo_prices()
            print(f"Using built-in synthetic prices for {len(tickers)} tickers and {len(dates)} dates.")

        returns = calculate_returns(prices)
        mean_returns = np.mean(returns, axis=0)
        covariance = np.cov(returns, rowvar=False, ddof=1)
        if np.ndim(covariance) == 0:
            covariance = np.array([[float(covariance)]])

        config = GeneticConfig(population_size=args.population, generations=args.generations)
        genetic = optimize_genetic(mean_returns, covariance, args.risk_limit, args.seed, config)
        markowitz = markowitz_portfolio(mean_returns, covariance, args.risk_limit)
        equal_weight = equal_weight_portfolio(mean_returns, covariance, args.risk_limit)
        results = [genetic, markowitz, equal_weight]

        _print_results(results, tickers, args.risk_limit)
        _save_results(results, tickers, args.risk_limit, args.output)
        print(f"Saved comparison to {args.output}.")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")


def _print_results(results, tickers: list[str], risk_limit: float) -> None:
    print(f"Risk limit: {risk_limit:.2%} annualized volatility")
    print(f"{'Method':<24} {'Return':>10} {'Risk':>10} {'Within limit':>15}")
    for result in results:
        print(
            f"{result.method:<24} {result.annual_return:>9.2%} "
            f"{result.annual_volatility:>9.2%} {str(result.feasible):>15}"
        )
        weights = ", ".join(f"{ticker}={weight:.1%}" for ticker, weight in zip(tickers, result.weights))
        print(f"  Weights: {weights}")


def _save_results(results, tickers: list[str], risk_limit: float, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["method", "annual_return", "annual_volatility", "risk_limit", "feasible", "weights"],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "method": result.method,
                    "annual_return": result.annual_return,
                    "annual_volatility": result.annual_volatility,
                    "risk_limit": risk_limit,
                    "feasible": result.feasible,
                    "weights": json.dumps(dict(zip(tickers, result.weights.tolist())), ensure_ascii=False),
                }
            )
