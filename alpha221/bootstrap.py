"""Block-bootstrap scenarios for six-month portfolio return estimates."""

import numpy as np


def sample_block_bootstrap(
    weekly_returns: np.ndarray,
    horizon_weeks: int = 26,
    block_length: int = 4,
    simulations: int = 10_000,
    seed: int = 42,
) -> np.ndarray:
    """Resample joint weekly return vectors in overlapping historical blocks."""
    returns = np.asarray(weekly_returns, dtype=float)
    if returns.ndim != 2 or returns.shape[0] < block_length or returns.shape[1] < 1:
        raise ValueError("Weekly returns must be a 2D array with at least one full block.")
    if not np.isfinite(returns).all() or np.any(returns <= -1.0):
        raise ValueError("Weekly returns must be finite and greater than -100%.")
    if horizon_weeks < 1 or block_length < 1 or simulations < 1:
        raise ValueError("Horizon, block length, and simulation count must be positive.")

    rng = np.random.default_rng(seed)
    block_count = int(np.ceil(horizon_weeks / block_length))
    starts = rng.integers(
        0,
        returns.shape[0] - block_length + 1,
        size=(simulations, block_count),
    )
    offsets = np.arange(block_length)
    indices = (starts[:, :, None] + offsets[None, None, :]).reshape(simulations, -1)
    indices = indices[:, :horizon_weeks]
    return returns[indices]


def positive_return_probabilities(
    weights: np.ndarray,
    scenarios: np.ndarray,
) -> np.ndarray:
    """Estimate P(compounded portfolio return > 0) for one or more weight vectors."""
    weight_matrix = np.asarray(weights, dtype=float)
    if weight_matrix.ndim == 1:
        weight_matrix = weight_matrix[None, :]
    sampled_returns = np.asarray(scenarios, dtype=float)
    if sampled_returns.ndim != 3:
        raise ValueError("Scenarios must have shape (simulations, weeks, assets).")
    if weight_matrix.ndim != 2 or weight_matrix.shape[1] != sampled_returns.shape[2]:
        raise ValueError("Weights and bootstrap scenarios must contain the same assets.")
    if not np.isfinite(weight_matrix).all() or np.any(weight_matrix < 0):
        raise ValueError("Portfolio weights must be finite and non-negative.")
    if not np.allclose(weight_matrix.sum(axis=1), 1.0, atol=1e-8):
        raise ValueError("Each portfolio's weights must sum to one.")
    if not np.isfinite(sampled_returns).all() or np.any(sampled_returns <= -1.0):
        raise ValueError("Scenario returns must be finite and greater than -100%.")

    probabilities = np.empty(len(weight_matrix), dtype=float)
    batch_size = 128
    for start in range(0, len(weight_matrix), batch_size):
        stop = min(start + batch_size, len(weight_matrix))
        batch = weight_matrix[start:stop]
        wealth = np.ones((len(batch), sampled_returns.shape[0]), dtype=float)
        for week in range(sampled_returns.shape[1]):
            portfolio_weekly_returns = batch @ sampled_returns[:, week, :].T
            wealth *= 1.0 + portfolio_weekly_returns
        probabilities[start:stop] = np.mean(wealth > 1.0, axis=1)
    return probabilities
