# Project Topic Card

**Group:** L2 / L3 · **Team:** Z4 · **Last updated:** 2026-11-14
Artificial Intelligence — Laboratory · Collegium Da Vinci · academic year 2026/2027

This is an English translation of the canonical Polish [`karta-tematu.md`](karta-tematu.md).

## 1. Team

| Name | Student ID | Initial role |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Working together; individual roles to be assigned later |
| Adam Remfeld | 31799 | Working together; individual roles to be assigned later |
| Nikodem Boniecki | 31865 | Working together; individual roles to be assigned later |

## 2. Title

- **Polish:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **English:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem

An individual investor choosing several stocks must decide how to distribute capital among them while balancing expected return and risk. The system will take daily historical prices for selected companies and a maximum risk level provided by the user. It will calculate proposed portfolio weights and estimate the portfolio's expected return and risk. The initial scope focuses on companies in AI, game development, and semiconductors.

## 4. Why an ordinary algorithm may not be enough

- [ ] We cannot express the rule step by step.
- [ ] A procedure exists, but is computationally too expensive.
- [ ] There are too many rules and they change over time.

The basic mean-variance portfolio problem can be solved with classical optimization, so we do not assume a conventional algorithm is insufficient for the planned number of stocks. We chose a genetic algorithm as the AI technique studied in the course and will compare it with the classical solution and a simple equal-weight portfolio.

## 5. AI technology

- [ ] Neural network
- [ ] Expert system / rule-based reasoning
- [x] Genetic algorithm
- [ ] Classical machine learning

A genetic algorithm can search many possible portfolio weight combinations and account for a risk limit when evaluating candidates. It will let us compare heuristic search with the analytical Markowitz solution.

## 6. Data

| | |
|---|---|
| Source | [Tiingo EOD Daily Prices API](https://www.tiingo.com/documentation/end-of-day), endpoint `/tiingo/daily/{ticker}/prices`; tickers and dates are still to be selected |
| Planned size and format | Approximately 50–100 tickers and up to five years of daily data; JSON API responses. Actual size depends on symbols and date range. |
| Data available? | No — data have not been downloaded and an API token has not been configured. |
| Acquisition plan | Create a Tiingo account, obtain a token, and download historical prices for the selected tickers. Store the token locally in an environment variable and do not commit downloaded data to the repository. |

## 7. Technology stack

The planned implementation uses Python 3 and runs on CPU. Planned libraries are `requests` for API access and `numpy` and `pandas` for price-series processing and calculations. Exact Python and dependency versions will be pinned when the project skeleton is created. Tiingo access requires an API token. The Starter plan labels the data for internal use, so raw data will not be committed or redistributed without checking the applicable permissions.

## 8. Success criterion

- **Metric:** Share of returned portfolios satisfying the annualized volatility cap, and the ratio of the genetic algorithm's annualized expected return to Markowitz under the same cap.
- **Numeric threshold:** 100% of returned portfolios must satisfy the risk limit, and median return relative to Markowitz must be at least 95% across five test cases. This is a provisional target to confirm before evaluation.
- **Baselines:** Classical Markowitz optimization (quality reference) and an equal-weight 1/N portfolio (simple baseline).

## 9. Minimum scope

The program will load historical prices for several tickers, calculate daily returns and a covariance matrix, run a custom genetic algorithm for long-only portfolios whose weights sum to one, and never return a portfolio that violates the risk limit. It will report portfolio weights, estimated return and risk, and compare results with Markowitz and 1/N on the same data.

## 10. Optional scope

Direct API download, comparison of multiple parameter settings and random seeds, an efficient frontier plot, and a simple interface for choosing tickers and a risk limit.

## 11. Repository

https://github.com/NikodemBoniecki/Alpha221

Sprint reports will be kept in `sprints.txt` at the repository root.

## 12. Main risk and fallback plan

The main risks are losing API access or encountering license restrictions, and failing to find a portfolio under an overly strict risk limit. We will first verify API access and data-use terms. If data download is unavailable, we will use clearly labeled synthetic test data with a fixed random seed. If the risk limit is infeasible for the selected assets, the program will report that no feasible solution was found instead of returning a portfolio that violates the constraint.
