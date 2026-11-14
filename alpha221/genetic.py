from dataclasses import dataclass

import numpy as np

from .portfolio import PortfolioResult, portfolio_stats


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


def _fitness(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
) -> tuple[float, float, float]:
    annual_return, annual_volatility = portfolio_stats(weights, mean_returns, covariance)
    if annual_volatility <= risk_limit:
        return annual_return, annual_return, annual_volatility
    return -1000.0 - (annual_volatility - risk_limit) * 1000.0, annual_return, annual_volatility


def optimize_genetic(
    mean_returns: np.ndarray,
    covariance: np.ndarray,
    risk_limit: float,
    seed: int,
    config: GeneticConfig = GeneticConfig(),
) -> PortfolioResult:
    rng = np.random.default_rng(seed)
    asset_count = len(mean_returns)
    population = rng.dirichlet(np.ones(asset_count), size=config.population_size)
    population[0] = np.full(asset_count, 1.0 / asset_count)
    best_feasible: tuple[float, np.ndarray, float] | None = None

    for _ in range(config.generations):
        scored = [_fitness(weights, mean_returns, covariance, risk_limit) for weights in population]
        fitness = np.array([item[0] for item in scored])

        for weights, (_, annual_return, annual_volatility) in zip(population, scored):
            if annual_volatility <= risk_limit and (
                best_feasible is None or annual_return > best_feasible[0]
            ):
                best_feasible = (annual_return, weights.copy(), annual_volatility)

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
            next_population.append(_normalize(child))

        population = np.asarray(next_population)

    for weights in population:
        _, annual_return, annual_volatility = _fitness(weights, mean_returns, covariance, risk_limit)
        if annual_volatility <= risk_limit and (
            best_feasible is None or annual_return > best_feasible[0]
        ):
            best_feasible = (annual_return, weights.copy(), annual_volatility)

    if best_feasible is None:
        raise ValueError("The genetic algorithm did not find a portfolio within the risk limit.")

    annual_return, weights, annual_volatility = best_feasible
    return PortfolioResult(
        method="Genetic algorithm",
        weights=weights,
        annual_return=annual_return,
        annual_volatility=annual_volatility,
        feasible=True,
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
