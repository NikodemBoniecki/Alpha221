# Project Topic Card

**Group:** L2 / L3 | **Team:** Z4 | **Last updated:** 2026-11-14
Artificial Intelligence laboratory | Collegium Da Vinci | academic year 2026/2027

This is an English translation of our main Polish [`karta-tematu.md`](karta-tematu.md).

## 1. Team

| Name | Student ID | Initial role |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Genetic algorithm design and operators |
| Adam Remfeld | 31799 | Choosing a licensed source, acquiring and preparing data |
| Nikodem Boniecki | 31865 | Baselines, evaluation, integration, and documentation |

## 2. Title

- **Polish:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **English:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem

We want to help individual investors decide how to divide money among selected stocks while balancing expected return and risk. Our program will use historical daily prices and a risk limit set by the user. It will suggest portfolio weights and estimate the portfolio's return and risk. We will start with companies in AI, game development, and semiconductors.

## 4. Why use AI for this problem?

- [ ] We cannot express the rule step by step.
- [ ] A standard procedure exists, but is too expensive to run.
- [ ] There are too many rules and they change over time.

We can solve the basic portfolio problem with standard mean-variance optimization, so we are not claiming that a conventional algorithm is too slow for our planned dataset. We chose a genetic algorithm to study the AI method from our course and compare it with Markowitz and an equal-weight portfolio.

## 5. AI technology

- [ ] Neural network
- [ ] Expert system or rule-based reasoning
- [x] Genetic algorithm
- [ ] Classical machine learning

A genetic algorithm lets us search many possible sets of portfolio weights and account for the risk limit when scoring them. We will compare its results with the analytical Markowitz solution.

## 6. Data

| | |
|---|---|
| Source | We have not selected a dataset yet. Tiingo EOD Daily Prices is one candidate: [documentation](https://www.tiingo.com/documentation/end-of-day), endpoint `/tiingo/daily/{ticker}/prices`. We still need to choose tickers and dates. See [`docs/tiingo-data-notes.md`](docs/tiingo-data-notes.md) for the license details. |
| Planned size and format | We are considering 50 to 100 tickers and up to five years of daily prices. The API returns JSON by default and also supports CSV. |
| Data available? | No. We have not selected or downloaded the dataset. |
| Acquisition plan | We will choose tickers and dates and check that each symbol is available. Before using Tiingo, we need an Enterprise license that allows storing the data and evaluating an AI system. Otherwise, we will choose another specific dataset with a license that allows this use. Starter and Power do not allow the planned benchmark. |

## 7. Technology stack

We plan to use Python 3 on CPU. We may use `requests` for API access and `numpy` and `pandas` for data processing and calculations. We will set the exact Python and library versions when we add the project skeleton. Tiingo requires an API token, but we will not download its data without a license for storage and AI evaluation. More details are in [`docs/tiingo-data-notes.md`](docs/tiingo-data-notes.md).

## 8. Success criterion

- **Metric:** Share of returned portfolios that meet the annualized volatility limit, and the genetic algorithm's annualized return compared with Markowitz under the same limit.
- **Threshold:** Every returned portfolio must meet the risk limit. Across five test cases, median return must reach at least 95% of the Markowitz result. This is our evaluation target.
- **Baselines:** Markowitz optimization and an equal-weight 1/N portfolio.

## 9. Minimum scope

Our program will load historical prices for several tickers, calculate daily returns and a covariance matrix, then run our genetic algorithm. It will allow long positions only and require portfolio weights to sum to one. It will report weights, estimated return, and risk, reject portfolios that exceed the risk limit, and compare results with Markowitz and 1/N on the same data.

## 10. Optional scope

If we have time, we will add direct API downloads, compare more parameter settings and random seeds, plot the efficient frontier, or build a simple screen for choosing tickers and the risk limit.

## 11. Repository

https://github.com/NikodemBoniecki/Alpha221

We will keep sprint reports in `sprints.txt` at the repository root.

## 12. Main risk and fallback plan

Our main risk is not getting a license that allows us to store and evaluate market data. We will check the data terms before downloading anything and use a suitably licensed dataset if Tiingo does not permit our planned use. If the risk limit is too low for the selected stocks, the program will report that no valid portfolio was found. We will use synthetic data to check the code only, not for the final evaluation.
