# Project Topic Card

**Group:** L2 / L3 | **Team:** Z4 | **Updated:** 2026-11-21
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

The project checks how different portfolio weights affect return and risk estimates. The user sets an annual volatility limit, and the program compares the genetic algorithm with Markowitz optimization and an equal-weight portfolio.

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

By default, the downloader gets two years of data for the 15 stocks, two ETFs, and the USDPLN=X and EURUSD=X currency pairs. A fixed `--start/--end` window can be used to reproduce a dataset. Historical adjusted prices are converted to USD: PLN prices are divided by USD/PLN, and EUR prices are multiplied by EUR/USD. Missing asset prices are not filled.

The seven-year dataset covers 2019-11-21 to 2026-11-20. It contains 1,703 common daily sessions and 366 weekly prices, or 365 return periods. We found no ticker or currency mismatches, gaps, or invalid prices. Every required FX rate came from the same date.

## 7. Technology stack

Python 3.10+, NumPy, SciPy, pandas, and yfinance. Run python -m alpha221.market_data to download data. No API token is required. The application is a command-line prototype.

## 8. Comparison criteria

GA looks for the highest estimated chance of a positive six-month USD return without exceeding the annual volatility limit. It selects exactly 10 of 15 stocks. Each selected stock has a weight between 1% and 20%; stocks together make up 80% of the portfolio. The two ETFs share the remaining 20%, with at least 1% in each. Markowitz follows the same limits but can use any number of stocks. The 1/N baseline divides both parts equally.

Weights are fitted on a rolling two-year window of weekly returns. The five-year walk-forward test recalculates them every 26 weeks and keeps each allocation for the next 26 weeks. The bootstrap uses four-week blocks and 1,000 paths while GA is running. The final report uses 10,000 paths and also checks two- and eight-week blocks. With a 22% risk limit, historical compounded returns were 199.71% for GA, 319.40% for Markowitz, and 177.29% for 1/N. Every method had 9 positive periods out of 10.

## 9. Scope and implementation status

The program can download and audit data, convert prices to USD, export daily and weekly files, save a SHA-256 manifest, and compare GA, Markowitz, and 1/N. It enforces the agreed weight limits, runs the five-year walk-forward test, and checks all 3,003 possible groups of 10 stocks.

The remaining task is to convert an investment amount in USD into units that can actually be bought. GA is the method studied in the project, not a method assumed to be better than Markowitz.

## 10. Limitations

Results depend on the chosen historical window and do not predict future prices. Transaction costs, taxes, and liquidity are not modelled. Yahoo Finance data are not guaranteed to be error-free or continuously available. Downloaded price series are not published. This project is not investment advice.

## 11. Repository

https://github.com/NikodemBoniecki/Alpha221
