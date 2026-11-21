# Alpha221: risk-constrained portfolio optimization

Artificial intelligence laboratory project at Collegium Da Vinci, group L2/L3, academic year 2026/2027.

[Polska wersja README](README_PL.md) · [Polish project card](project_card_PL.md) · [Technical documentation](docs/dokumentacja.md)

## Goal

The program compares a genetic algorithm (GA), Markowitz optimization, and a simple 1/N portfolio on the same prices. The basket contains 15 stocks and two ETFs: SPY and ETFBW20TR.WA. GA selects exactly 10 stocks and assigns them 80% of the portfolio, with 1-20% in each selected stock. The ETFs receive the remaining 20%, with at least 1% in each. GA maximizes the estimated chance of a positive six-month USD return without exceeding the volatility limit. Markowitz uses the same budgets but does not have to select exactly 10 stocks. The 1/N portfolio splits both buckets equally.

## Data

The downloader gets Yahoo Finance data through yfinance. It converts historical `Adj Close` prices to USD with the FX rate from the same date and never fills missing asset prices. The audit checks the ticker, currency, instrument type, exchange time zone, dividends, splits, and FX alignment. It also records the actual source date of every weekly price.

The final seven-year window from 2019-11-21 through 2026-11-20 contains 1,703 complete common daily sessions and 366 weekly prices for all 17 instruments. It has no missing, duplicate, or non-positive prices and no gaps in the weekly index. Every required FX observation was available on the same date. Generated data and audit files remain local and are ignored by Git.

The default two-year command was verified on 2026-11-21 and produced 485 common daily sessions and 105 weekly prices (104 return intervals) through 2026-11-20.

## Run

Python 3.10 or newer is required. The instructions were verified with Python 3.12.10.

~~~bash
python -m pip install -r requirements.txt
python -m alpha221.market_data
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22
~~~

The default download uses a relative `2y` period. It writes adjusted daily USD prices to `data/prices.csv`, weekly prices to `data/prices_weekly_usd.csv`, latest closes to `data/latest_prices_usd.csv`, the instrument audit to `results/market_data_audit.csv`, the calendar audit to `results/market_data_calendar_audit.csv`, and the reproducibility manifest to `data/market_data_manifest.json`.

Reproduce the fixed seven-year evaluation dataset:

~~~bash
python -m alpha221.market_data --start 2019-11-21 --end 2026-11-21 --minimum-common-rows 1600 --prices-output data/raw/prices_7y_usd.csv --weekly-output data/raw/prices_weekly_7y_usd.csv --latest-output data/raw/latest_prices_7y_usd.csv --audit-output results/market_data_audit_7y.csv --calendar-audit-output results/market_data_calendar_audit_7y.csv --manifest-output data/raw/market_data_manifest_7y.json
~~~

Run the five-year out-of-sample evaluation:

~~~bash
python -m alpha221 --input data/raw/prices_weekly_7y_usd.csv --frequency weekly --risk-limit 0.22 --walk-forward --fold-output results/walk_forward_folds_7y.csv --summary-output results/walk_forward_summary_7y.csv
~~~

The comparison command runs the weekly optimizer with the project's 80/20 allocation, GA cardinality rule, and bootstrap probability objective. It uses the two-year input and is an in-sample estimate; use the seven-year walk-forward command in the technical documentation for out-of-sample evaluation. Weekly sampling annualizes with 52 periods; daily sampling uses 252:

~~~bash
python -m alpha221 --input data/prices.csv --frequency daily --risk-limit 0.22
~~~

Without an input file, python -m alpha221 uses synthetic demo prices.

## Project status

Data download, auditing, currency conversion, portfolio constraints, weekly bootstrap, walk-forward testing, and the check of all 3,003 stock subsets are complete. In the historical test, GA returned 199.71%, Markowitz 319.40%, and 1/N 177.29%. Each method made a profit in 9 of 10 periods. The results exclude trading costs and taxes. Converting an investment amount into asset units is still missing.

## Data source and limits

yfinance is an unofficial tool that uses Yahoo Finance's publicly available interfaces. This is an educational project, not an investment product. Yahoo places restrictions on data use and redistribution; downloaded price series are not published. See the [technical documentation](docs/dokumentacja.md).
