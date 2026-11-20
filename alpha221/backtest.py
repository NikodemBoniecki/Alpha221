"""Rolling out-of-sample evaluation for the agreed weekly portfolio design."""

import json
from datetime import date

import numpy as np

from .bootstrap import positive_return_probabilities, sample_block_bootstrap
from .data import calculate_returns
from .genetic import GeneticConfig, optimize_genetic
from .portfolio import equal_weight_portfolio, markowitz_portfolio
from .universe import ASSETS


STOCK_COUNT = 15
ASSET_COUNT = 17
TRAINING_WEEKS = 104
HOLDING_WEEKS = 26
STEP_WEEKS = 26
BLOCK_LENGTHS = (2, 4, 8)


def run_walk_forward(
    tickers: list[str],
    dates: list[date],
    prices: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig,
    reporting_simulations: int = 10_000,
    optimization_simulations: int = 1_000,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Fit on trailing 104 weekly returns, then score the next 26 weeks."""
    if tickers != ASSETS or prices.shape[1] != ASSET_COUNT:
        raise ValueError("Walk-forward evaluation requires the project's 15 stocks and two ETFs.")
    if len(dates) != len(prices):
        raise ValueError("Each price row must have a matching date.")
    returns = calculate_returns(prices)
    last_start = len(returns) - TRAINING_WEEKS - HOLDING_WEEKS
    starts = range(0, last_start + 1, STEP_WEEKS)
    if last_start < 0:
        raise ValueError("Walk-forward input needs at least 130 weekly return observations.")

    fold_rows: list[dict[str, object]] = []
    method_actual_returns: dict[str, list[np.ndarray]] = {}
    method_predicted_probabilities: dict[str, list[float]] = {}
    method_fold_volatility: dict[str, list[float]] = {}

    for fold_number, start in enumerate(starts, start=1):
        train_end = start + TRAINING_WEEKS
        test_end = train_end + HOLDING_WEEKS
        training_returns = returns[start:train_end]
        test_returns = returns[train_end:test_end]
        if len(test_returns) != HOLDING_WEEKS:
            continue

        mean_returns = np.mean(training_returns, axis=0)
        covariance = np.cov(training_returns, rowvar=False, ddof=1)
        scenarios_for_fit = sample_block_bootstrap(
            training_returns,
            horizon_weeks=HOLDING_WEEKS,
            block_length=4,
            simulations=optimization_simulations,
            seed=seed + fold_number,
        )
        genetic = optimize_genetic(
            mean_returns,
            covariance,
            risk_limit,
            seed + fold_number,
            config,
            52,
            scenarios_for_fit,
            enforce_project_constraints=True,
        )
        markowitz = markowitz_portfolio(
            mean_returns,
            covariance,
            risk_limit,
            52,
            stock_count=STOCK_COUNT,
        )
        equal_weight = equal_weight_portfolio(
            mean_returns,
            covariance,
            risk_limit,
            52,
            stock_count=STOCK_COUNT,
        )
        methods = [genetic, markowitz, equal_weight]

        report_scenarios = {
            block_length: sample_block_bootstrap(
                training_returns,
                horizon_weeks=HOLDING_WEEKS,
                block_length=block_length,
                simulations=reporting_simulations,
                seed=seed + 100_000 + fold_number * 10 + block_length,
            )
            for block_length in BLOCK_LENGTHS
        }
        for result in methods:
            predicted = {
                block_length: float(
                    positive_return_probabilities(result.weights, scenarios)[0]
                )
                for block_length, scenarios in report_scenarios.items()
            }
            realized_weekly = test_returns @ result.weights
            realized_six_month = float(np.prod(1.0 + realized_weekly) - 1.0)
            realized_volatility = float(np.std(realized_weekly, ddof=1) * np.sqrt(52.0))
            test_start_date = dates[train_end]
            test_end_date = dates[test_end]
            method_actual_returns.setdefault(result.method, []).append(realized_weekly)
            method_predicted_probabilities.setdefault(result.method, []).append(predicted[4])
            method_fold_volatility.setdefault(result.method, []).append(realized_volatility)
            fold_rows.append(
                {
                    "fold": fold_number,
                    "method": result.method,
                    "training_start": dates[start].isoformat(),
                    "training_end": dates[train_end].isoformat(),
                    "test_start": test_start_date.isoformat(),
                    "test_end": test_end_date.isoformat(),
                    "estimated_probability_block2": predicted[2],
                    "estimated_probability_block4": predicted[4],
                    "estimated_probability_block8": predicted[8],
                    "estimated_annual_volatility": result.annual_volatility,
                    "realized_six_month_return": realized_six_month,
                    "positive_six_month_return": realized_six_month > 0.0,
                    "realized_annualized_volatility": realized_volatility,
                    "risk_limit": risk_limit,
                    "within_realized_risk_limit": realized_volatility <= risk_limit,
                    "weights": json.dumps(
                        dict(zip(tickers, result.weights.tolist())), ensure_ascii=False
                    ),
                }
            )

    summary_rows: list[dict[str, object]] = []
    for method, weekly_periods in method_actual_returns.items():
        concatenated = np.concatenate(weekly_periods)
        period_returns = [float(np.prod(1.0 + item) - 1.0) for item in weekly_periods]
        summary_rows.append(
            {
                "method": method,
                "six_month_periods": len(period_returns),
                "five_year_compounded_return": float(np.prod(1.0 + concatenated) - 1.0),
                "positive_periods": sum(value > 0.0 for value in period_returns),
                "positive_period_rate": float(np.mean(np.array(period_returns) > 0.0)),
                "mean_estimated_probability_block4": float(
                    np.mean(method_predicted_probabilities[method])
                ),
                "realized_annualized_volatility": float(np.std(concatenated, ddof=1) * np.sqrt(52.0)),
                "periods_with_realized_risk_within_limit": sum(
                    value <= risk_limit for value in method_fold_volatility[method]
                ),
                "risk_limit": risk_limit,
            }
        )
    if not fold_rows:
        raise ValueError("No complete 26-week out-of-sample periods were available.")
    return fold_rows, summary_rows
