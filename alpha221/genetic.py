from dataclasses import dataclass

import numpy as np

from .bootstrap import positive_return_probabilities
from .portfolio import PortfolioResult


@dataclass(frozen=True)
class GeneticConfig:
    population_size: int = 100
    generations: int = 200
    tournament_size: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    mutation_scale: float = 0.05


def _normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.clip(weights, 0.0, None)
    total = float(np.sum(weights))
    if total <= 0:
        return np.full(len(weights), 1.0 / len(weights))
    return weights / total


def _bounded_simplex(
    values: np.ndarray,
    total: float,
    lower: float,
    upper: float,
) -> np.ndarray:
    """Project genes onto a bounded simplex using a one-dimensional search."""
    values = np.maximum(np.asarray(values, dtype=float), 0.0)
    if lower * len(values) > total or upper * len(values) < total:
        raise ValueError("Weight bounds cannot satisfy the requested portfolio budget.")

    left = float(np.min(values - upper))
    right = float(np.max(values - lower))
    for _ in range(80):
        shift = (left + right) / 2.0
        projected = np.clip(values - shift, lower, upper)
        if projected.sum() > total:
            left = shift
        else:
            right = shift
    projected = np.clip(values - (left + right) / 2.0, lower, upper)
    projected *= total / projected.sum()
    return projected


def repair_chromosome(chromosome: np.ndarray) -> np.ndarray:
    """Enforce 10 selected stocks, the 80/20 split, and agreed weight bounds."""
    genes = np.asarray(chromosome, dtype=float)
    if genes.shape != (17,) or not np.isfinite(genes).all():
        raise ValueError("Target portfolios require 17 finite asset genes.")

    stock_count = 15
    selected = np.argsort(genes[:stock_count], kind="stable")[-10:]
    repaired = np.zeros_like(genes)
    repaired[selected] = _bounded_simplex(genes[selected], 0.80, 0.01, 0.20)
    repaired[stock_count:] = _bounded_simplex(genes[stock_count:], 0.20, 0.01, 0.19)
    return repaired


def optimize_genetic(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig = GeneticConfig(),
    periods_per_year: int = 252,
    bootstrap_scenarios: np.ndarray | None = None,
    enforce_project_constraints: bool = False,
) -> PortfolioResult:
    rng = np.random.default_rng(seed)
    asset_count = len(mean_returns)
    population = rng.dirichlet(np.ones(asset_count), size=config.population_size)
    if enforce_project_constraints:
        if asset_count != 17:
            raise ValueError("Project portfolio rules require the fixed 17-asset universe.")
        population = np.array([repair_chromosome(row) for row in population])
        population[0] = repair_chromosome(np.ones(asset_count))
    else:
        population[0] = np.full(asset_count, 1.0 / asset_count)
    best_feasible: tuple[float, np.ndarray, float, float | None] | None = None

    for _ in range(config.generations):
        annual_returns = population @ mean_returns * periods_per_year
        variances = np.einsum("pi,ij,pj->p", population, covariance, population)
        annual_volatilities = np.sqrt(np.maximum(variances * periods_per_year, 0.0))
        if bootstrap_scenarios is None:
            probabilities = None
            fitness = annual_returns.copy()
        else:
            probabilities = positive_return_probabilities(population, bootstrap_scenarios)
            fitness = probabilities + np.clip(annual_returns, -1.0, 1.0) * 1e-6
        feasible = annual_volatilities <= risk_limit
        fitness[~feasible] = -1000.0 - (annual_volatilities[~feasible] - risk_limit) * 1000.0

        for index in np.flatnonzero(feasible):
            objective = (
                float(probabilities[index]) if probabilities is not None else float(annual_returns[index])
            )
            if best_feasible is None or objective > best_feasible[0]:
                probability = float(probabilities[index]) if probabilities is not None else None
                best_feasible = (
                    objective,
                    population[index].copy(),
                    float(annual_volatilities[index]),
                    probability,
                )

        elite_count = max(1, config.population_size // 20)
        elite_indices = np.argsort(fitness)[-elite_count:]
        next_population = [population[index].copy() for index in elite_indices]

        while len(next_population) < config.population_size:
            first = _tournament(population, fitness, rng, config.tournament_size)
            second = _tournament(population, fitness, rng, config.tournament_size)

            if rng.random() < config.crossover_rate:
                amount = rng.random()
                child = amount * first + (1.0 - amount) * second
            else:
                child = first.copy()

            if rng.random() < config.mutation_rate:
                child += rng.normal(0.0, config.mutation_scale, size=asset_count)
            if enforce_project_constraints:
                next_population.append(repair_chromosome(child))
            else:
                next_population.append(_normalize(child))

        population = np.asarray(next_population)

    annual_returns = population @ mean_returns * periods_per_year
    variances = np.einsum("pi,ij,pj->p", population, covariance, population)
    annual_volatilities = np.sqrt(np.maximum(variances * periods_per_year, 0.0))
    probabilities = (
        positive_return_probabilities(population, bootstrap_scenarios)
        if bootstrap_scenarios is not None
        else None
    )
    for index in np.flatnonzero(annual_volatilities <= risk_limit):
        objective = (
            float(probabilities[index]) if probabilities is not None else float(annual_returns[index])
        )
        if best_feasible is None or objective > best_feasible[0]:
            probability = float(probabilities[index]) if probabilities is not None else None
            best_feasible = (
                objective,
                population[index].copy(),
                float(annual_volatilities[index]),
                probability,
            )

    if best_feasible is None:
        raise ValueError("The genetic algorithm did not find a portfolio within the risk limit.")

    _, weights, annual_volatility, probability = best_feasible
    annual_return = float(np.dot(mean_returns, weights) * periods_per_year)
    return PortfolioResult(
        method="Genetic algorithm",
        weights=weights,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        feasible=True,
        probability_positive_6m=probability,
    )


def _tournament(
    population: np.ndarray,
    fitness: np.ndarray,
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:
    participants = rng.choice(len(population), size=min(size, len(population)), replace=False)
    winner = participants[np.argmax(fitness[participants])]
    return population[winner]
