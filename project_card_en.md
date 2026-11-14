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
| Source | [Huge Stock Market Dataset, version 3](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs). We plan to use the NVDA, AMD, MSFT, EA, and TTWO files. The dataset is marked CC0. |
| Planned size and format | Five CSV files with daily OHLCV data. Planned dates are 2012-01-03 to 2017-01-03, about 1,260 sessions per stock or about 6,300 observations before checking gaps. |
| Data available? | No. We have selected the dataset but have not downloaded the files. |
| Acquisition plan | We will download the five files from Kaggle, check ticker and date coverage, then prepare one wide CSV with dates and adjusted closing prices. Kaggle describes the prices as adjusted for splits and dividends. |

## 7. Technology stack

The program runs on Python 3.10 or newer and CPU. It uses `numpy` and `scipy` for calculations; dependencies are listed in `requirements.txt`. We will download the data from Kaggle manually and load a prepared CSV file. The project does not use an API token.

## 8. Success criterion

- **Metric:** Share of GA portfolios that meet the annualized volatility limit, and the annual GA to Markowitz return ratio under the same limit.
- **Threshold:** Every portfolio returned by the genetic algorithm must meet the risk limit. The median of five annual GA to Markowitz return ratios, one for each year from 2012 to 2016, must be at least 0.95 (95%). This is our evaluation target.
- **Baselines:** Markowitz optimization and an equal-weight 1/N portfolio.

## 9. Minimum scope

Our program will load historical prices for several tickers, calculate daily returns and a covariance matrix, then run our genetic algorithm. It will allow long positions only and require portfolio weights to sum to one. It will report weights, estimated return, and risk, reject portfolios that exceed the risk limit, and compare results with Markowitz and 1/N on the same data.

## 10. Optional scope

If we have time, we will compare more parameter settings and random seeds, plot the efficient frontier, or build a simple screen for choosing tickers and the risk limit.

## 11. Repository

https://github.com/NikodemBoniecki/Alpha221

We will keep sprint reports in `sprints.txt` at the repository root.

## 12. Main risk and fallback plan

Our main risk is that some selected tickers may not cover the same dates or that the old dataset may not represent the current market. We will check the files and common date range before evaluation. If coverage is insufficient, we will use another CC0 stock dataset or reduce the ticker set. If the risk limit is too low, the program will report that no valid portfolio was found. Synthetic data is only for checking the code.
