"""Exhaustive cardinality benchmark using Markowitz weights per stock subset."""

from itertools import combinations
from collections.abc import Callable

import numpy as np
from scipy.optimize import minimize

from .bootstrap import positive_return_probabilities
from .portfolio import PortfolioResult


def exhaustive_subset_markowitz(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
    periods_per_year: int,
    scenarios: np.ndarray,
    progress: Callable[[int, int], None] | None = None,
) -> PortfolioResult:
    """Optimize conventional Markowitz weights for all 10-of-15 subsets.

    Each candidate invests 80% in ten selected stocks and 20% in both ETFs,
    with the project's selected-stock and ETF bounds. Candidates are ranked
    by bootstrap probability after the per-subset expected-return optimization.
    """
    if len(mean_returns) != 17 or covariance.shape != (17, 17):
        raise ValueError("Exhaustive subset search requires the fixed 17-asset universe.")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive.")

    subsets = list(combinations(range(15), 10))
    candidate_weights: list[np.ndarray] = []
    candidate_returns: list[float] = []
    candidate_volatilities: list[float] = []
    initial = np.array([0.08] * 10 + [0.10, 0.10])
    bounds = [(0.01, 0.20)] * 10 + [(0.01, 0.19)] * 2

    for subset_number, subset in enumerate(subsets, start=1):
        active_indices = list(subset) + [15, 16]
        subset_mean = mean_returns[active_indices]
        subset_covariance = covariance[np.ix_(active_indices, active_indices)]
        constraints = [
            {"type": "eq", "fun": lambda weights: np.sum(weights[:10]) - 0.80},
            {"type": "eq", "fun": lambda weights: np.sum(weights[10:]) - 0.20},
            {
                "type": "ineq",
                "fun": lambda weights, cov=subset_covariance: risk_limit
                - np.sqrt(max(float(weights @ cov @ weights * periods_per_year), 0.0)),
            },
        ]
        optimized = minimize(
            lambda weights, mu=subset_mean: -float(mu @ weights),
            initial,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 200, "ftol": 1e-9},
        )
        if not optimized.success:
            if progress is not None and subset_number % 250 == 0:
                progress(subset_number, len(subsets))
            continue

        active_weights = np.asarray(optimized.x, dtype=float)
        annual_return = float(subset_mean @ active_weights * periods_per_year)
        annual_variance = float(
            active_weights @ subset_covariance @ active_weights * periods_per_year
        )
        annual_volatility = float(np.sqrt(max(annual_variance, 0.0)))
        if annual_volatility > risk_limit + 1e-6:
            if progress is not None and subset_number % 250 == 0:
                progress(subset_number, len(subsets))
            continue

        full_weights = np.zeros(17, dtype=float)
        full_weights[active_indices] = active_weights
        candidate_weights.append(full_weights)
        candidate_returns.append(annual_return)
        candidate_volatilities.append(annual_volatility)
        if progress is not None and subset_number % 250 == 0:
            progress(subset_number, len(subsets))

    if progress is not None and len(subsets) % 250:
        progress(len(subsets), len(subsets))

    if not candidate_weights:
        raise ValueError("No feasible subset Markowitz candidates were found under the risk limit.")

    weights_matrix = np.asarray(candidate_weights)
    probabilities = positive_return_probabilities(weights_matrix, scenarios)
    best_probability = float(np.max(probabilities))
    tied = np.flatnonzero(np.isclose(probabilities, best_probability, atol=1e-12))
    best_index = max(
        tied,
        key=lambda index: (
            candidate_returns[index],
            -candidate_volatilities[index],
        ),
    )
    return PortfolioResult(
        method="Exhaustive subset Markowitz",
        weights=weights_matrix[best_index],
        annual_return=candidate_returns[best_index],
        annual_volatility=candidate_volatilities[best_index],
        feasible=True,
        probability_positive_6m=float(probabilities[best_index]),
        candidate_subsets=len(subsets),
        feasible_candidate_subsets=len(candidate_weights),
    )
