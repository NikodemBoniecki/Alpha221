# Project Topic Card

**Group:** L2 / L3 | **Team:** Z4 | **Updated:** 2026-11-20
Artificial Intelligence laboratory | Collegium Da Vinci | academic year 2026/2027

## 1. Team

| Name | Student ID | Area |
|---|---:|---|
| Kacper Nowaczyk | 31838 | Genetic algorithm and operators |
| Adam Remfeld | 31799 | Data acquisition and preparation |
| Nikodem Boniecki | 31865 | Baselines, evaluation, integration, and documentation |

## 2. Title

- **Polish:** Optymalizator portfela inwestycyjnego algorytmem genetycznym przy ograniczeniu ryzyka
- **English:** Genetic Algorithm for Risk-Constrained Investment Portfolio Optimization

## 3. Problem

The project studies how portfolio allocation affects estimated return and risk. The user supplies an annual volatility limit. The program is intended to select asset weights and compare the genetic algorithm with Markowitz optimization and an equal-weight portfolio.

## 4. Why use a genetic algorithm?

The basic mean-variance portfolio problem can be solved without a genetic algorithm. We chose GA as the method studied in our course and as a comparison for a mixed asset-selection and weight-allocation problem.

## 5. AI technology

- [ ] Neural network
- [ ] Expert system or rule-based reasoning
- [x] Genetic algorithm
- [ ] Classical machine learning

## 6. Data

Daily quotes come from Yahoo Finance through the unofficial yfinance library. We use them only in a closed educational project. CSV price files are local and ignored by Git.

| Group | Ticker | Quote currency |
|---|---|---|
| Stocks | AAPL, MSFT, NVDA, JPM, KO, TTWO, AMD, ASML, TSLA | USD |
| Stock | UBI.PA | EUR |
| Stocks | CDR.WA, XTB.WA, PKN.WA, ASB.WA, CBF.WA | PLN |
| S&P 500 ETF | SPY | USD |
| WIG20TR ETF | ETFBW20TR.WA | PLN |

The downloader retrieves the latest two years for the 15 stocks, two ETFs, and USDPLN=X and EURUSD=X currency pairs. It converts corporate-action-adjusted historical prices to USD: PLN prices are divided by USD/PLN, and EUR prices are multiplied by EUR/USD. FX is aligned to each asset date; if an exact-date rate is unavailable, the most recent earlier rate is used. Asset prices are never filled.

The snapshot validated on 2026-11-20 contains 485 complete common daily sessions and 105 weekly prices, or 104 weekly return intervals. Each weekly price comes from the last common session of that week; its date label is the Friday ending the week.

## 7. Technology stack

Python 3.10+, NumPy, SciPy, pandas, and yfinance. Run python -m alpha221.market_data to download data. No API token is required. The application is a command-line prototype.

## 8. Comparison criteria

The GA objective is to maximize estimated probability of a positive compounded USD return over six months, subject to the supplied annualized volatility limit. The GA selects exactly 10 of 15 stocks; each selected stock has a 1% minimum and 20% maximum portfolio weight. Stocks total 80%; the two ETFs total 20%, with at least 1% in each. Markowitz uses the same 80/20 budgets, 20% stock cap, and ETF minimums, but has no exact-10 requirement. The 1/N baseline divides the stock budget equally across all 15 stocks and the ETF budget equally across both ETFs.

Weights are intended to use a rolling two-year weekly lookback. Evaluation is planned as a five-year out-of-sample walk-forward test, re-optimizing every 26 weeks and holding each allocation for the next 26 weeks. A seven-year dataset has been downloaded and validated. The weekly prototype now estimates six-month probability using a moving block bootstrap: four-week blocks, 1,000 paths during GA optimization, and 10,000 paths for reporting, with two- and eight-week sensitivity checks. Final results are not available yet.

## 9. Scope and implementation status

**Implemented:** data download and validation, USD conversion, daily and weekly price exports, CSV loading, prototype GA, Markowitz, 1/N, and daily/weekly annualization.

**Implemented:** agreed allocation/weight constraints, exact-10 GA selection, six-month block-bootstrap objective, rolling five-year evaluation, and exhaustive evaluation of all 3,003 stock subsets. **Still to implement:** converting a USD investment amount into asset units.

The target allocation rules and walk-forward evaluation are implemented. Exactly 10 of 15 stocks gives 3,003 possible subsets, so the GA should be presented as the method under study, not as inherently superior to Markowitz. Exhaustive subset search remains a useful next quality check.

## 10. Limitations

Results depend on the chosen historical window and do not predict future prices. Transaction costs, taxes, and liquidity are not modelled. Yahoo Finance data are not guaranteed to be error-free or continuously available. Downloaded price series are not published. This project is not investment advice.

## 11. Repository

https://github.com/NikodemBoniecki/Alpha221
