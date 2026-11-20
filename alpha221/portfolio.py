from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


DAILY_PERIODS_PER_YEAR = 252


@dataclass(frozen=True)
class PortfolioResult:
    method: str
    weights: np.ndarray
    annual_return: float
    annual_volatility: float
    feasible: bool
    probability_positive_6m: float | None = None
    probability_sensitivity: dict[int, float] | None = None
    candidate_subsets: int | None = None
    feasible_candidate_subsets: int | None = None


def portfolio_stats(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    periods_per_year: int = DAILY_PERIODS_PER_YEAR,
) -> tuple[float, float]:
    annual_return = float(np.dot(mean_returns, weights) * periods_per_year)
    variance = float(weights @ covariance @ weights * periods_per_year)
    annual_volatility = float(np.sqrt(max(variance, 0.0)))
    return annual_return, annual_volatility


def equal_weight_portfolio(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
    periods_per_year: int = DAILY_PERIODS_PER_YEAR,
    stock_count: int | None = None,
) -> PortfolioResult:
    weights = np.full(len(mean_returns), 1.0 / len(mean_returns))
    if stock_count is not None:
        if stock_count <= 0 or stock_count >= len(mean_returns):
            raise ValueError("stock_count must leave at least one ETF in the portfolio.")
        weights[:stock_count] = 0.80 / stock_count
        weights[stock_count:] = 0.20 / (len(mean_returns) - stock_count)
    annual_return, annual_volatility = portfolio_stats(
        weights, mean_returns, covariance, periods_per_year
    )
    return PortfolioResult(
        method="Equal weight (1/N)",
        weights=weights,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        feasible=annual_volatility <= risk_limit + 1e-8,
    )


def markowitz_portfolio(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
    periods_per_year: int = DAILY_PERIODS_PER_YEAR,
    stock_count: int | None = None,
) -> PortfolioResult:
    asset_count = len(mean_returns)
    initial = np.full(asset_count, 1.0 / asset_count)
    bounds = [(0.0, 1.0)] * asset_count
    constraints = [{"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0}]
    if stock_count is not None:
        if stock_count <= 0 or stock_count >= asset_count:
            raise ValueError("stock_count must leave at least one ETF in the portfolio.")
        etf_count = asset_count - stock_count
        initial[:stock_count] = 0.80 / stock_count
        initial[stock_count:] = 0.20 / etf_count
        bounds = [(0.0, 0.20)] * stock_count + [(0.01, 0.19)] * etf_count
        constraints = [
            {"type": "eq", "fun": lambda weights: np.sum(weights[:stock_count]) - 0.80},
            {"type": "eq", "fun": lambda weights: np.sum(weights[stock_count:]) - 0.20},
        ]

    minimum_risk = minimize(
        lambda weights: float(weights @ covariance @ weights),
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    min_return, min_volatility = portfolio_stats(
        minimum_risk.x, mean_returns, covariance, periods_per_year
    )
    if not minimum_risk.success or min_volatility > risk_limit + 1e-6:
        raise ValueError(
            f"Risk limit is too low. The lowest estimated portfolio risk is {min_volatility:.2%}."
        )

    risk_constraint = {
        "type": "ineq",
        "fun": lambda weights: risk_limit
        - portfolio_stats(weights, mean_returns, covariance, periods_per_year)[1],
    }
    result = minimize(
        lambda weights: -float(np.dot(mean_returns, weights)),
        minimum_risk.x,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints + [risk_constraint],
        options={"maxiter": 1000, "ftol": 1e-10},
    )

    weights = np.clip(result.x, 0.0, 1.0)
    weights = weights / weights.sum()
    annual_return, annual_volatility = portfolio_stats(
        weights, mean_returns, covariance, periods_per_year
    )
    if not result.success or annual_volatility > risk_limit + 1e-5:
        raise RuntimeError(f"Markowitz optimization did not find a feasible result: {result.message}")

    return PortfolioResult(
        method="Markowitz",
        weights=weights,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        feasible=True,
    )
