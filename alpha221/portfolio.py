from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


TRADING_DAYS = 252


@dataclass(frozen=True)
class PortfolioResult:
    method: str
    weights: np.ndarray
    annual_return: float
    annual_volatility: float
    feasible: bool


def portfolio_stats(weights: np.ndarray, mean_returns: np.ndarray, covariance: np.ndarray) -> tuple[float, float]:
    annual_return = float(np.dot(mean_returns, weights) * TRADING_DAYS)
    variance = float(weights @ covariance @ weights * TRADING_DAYS)
    annual_volatility = float(np.sqrt(max(variance, 0.0)))
    return annual_return, annual_volatility


def equal_weight_portfolio(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
) -> PortfolioResult:
    weights = np.full(len(mean_returns), 1.0 / len(mean_returns))
    annual_return, annual_volatility = portfolio_stats(weights, mean_returns, covariance)
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
) -> PortfolioResult:
    asset_count = len(mean_returns)
    initial = np.full(asset_count, 1.0 / asset_count)
    bounds = [(0.0, 1.0)] * asset_count
    budget_constraint = {"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0}

    minimum_risk = minimize(
        lambda weights: float(weights @ covariance @ weights),
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=[budget_constraint],
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    min_return, min_volatility = portfolio_stats(minimum_risk.x, mean_returns, covariance)
    if not minimum_risk.success or min_volatility > risk_limit + 1e-6:
        raise ValueError(
            f"Risk limit is too low. The lowest estimated portfolio risk is {min_volatility:.2%}."
        )

    risk_constraint = {
        "type": "ineq",
        "fun": lambda weights: risk_limit - portfolio_stats(weights, mean_returns, covariance)[1],
    }
    result = minimize(
        lambda weights: -float(np.dot(mean_returns, weights)),
        minimum_risk.x,
        method="SLSQP",
        bounds=bounds,
        constraints=[budget_constraint, risk_constraint],
        options={"maxiter": 1000, "ftol": 1e-10},
    )

    weights = np.clip(result.x, 0.0, 1.0)
    weights = weights / weights.sum()
    annual_return, annual_volatility = portfolio_stats(weights, mean_returns, covariance)
    if not result.success or annual_volatility > risk_limit + 1e-5:
        raise RuntimeError(f"Markowitz optimization did not find a feasible result: {result.message}")

    return PortfolioResult(
        method="Markowitz",
        weights=weights,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        feasible=True,
    )
