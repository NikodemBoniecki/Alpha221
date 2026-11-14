# Alpha221 — Genetic Algorithm for Portfolio Optimization

AI course project — Collegium Da Vinci, Computer Science, group L2 / L3, academic year 2026/2027.

[Polska wersja README](README_PL.md) · [Project card](karta-tematu.md) · [Project card (English translation)](project_card_en.md)

## What it does

Alpha221 is planned as a portfolio optimizer for retail investors choosing stocks, with an initial focus on AI, game development, and semiconductor companies. It will take historical stock prices and a user-defined risk limit, then return portfolio weights intended to maximize expected return while respecting that limit.

## AI technique

The project will implement a genetic algorithm from scratch. It fits this search problem because it can explore portfolio weights under a risk constraint; the fitness function will reward expected return and strongly penalize solutions that exceed the risk limit.

## Results

Results have not been measured yet because the implementation has not started. The genetic algorithm will be evaluated on the same test data as a Markowitz mean-variance optimizer and an equal-weight (1/N) portfolio.

## How to run

The repository does not contain runnable code yet. Python version, dependencies, data setup, entry point, and output location will be documented when the project skeleton is added. The planned data source is Tiingo EOD; using its API will require a Tiingo API token.

## Team

- Kacper Nowaczyk — working with the whole team; individual roles to be assigned later.
- Adam Remfeld — working with the whole team; individual roles to be assigned later.
- Nikodem Boniecki — working with the whole team; individual roles to be assigned later.

## Documentation

Project documentation: [full documentation in Polish](docs/dokumentacja.md) and [technical abstract in English](docs/abstract_en.md).
