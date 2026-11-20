# Alpha221: risk-constrained portfolio optimization

Artificial intelligence laboratory project at Collegium Da Vinci, group L2/L3, academic year 2026/2027.

[Polska wersja README](README_PL.md) · [Polish project card](project_card_PL.md) · [Technical documentation](docs/dokumentacja.md)

## Goal

We compare a genetic algorithm (GA), Markowitz optimization, and an equal-weight 1/N portfolio on the same price data. The basket contains 15 stocks and two ETFs: SPY for the S&P 500 and ETFBW20TR.WA for WIG20TR. The GA allocates 80% to exactly 10 selected stocks (1–20% of total portfolio each) and 20% to the ETFs (at least 1% each), maximizing estimated probability of a positive USD return over six months subject to an annualized volatility limit. Markowitz uses the same allocation and 20% stock cap without an exact-10 constraint; 1/N equally weights all stocks and ETFs within their buckets. Weekly block-bootstrap estimation, target weight constraints, and the five-year walk-forward evaluation are implemented. The first out-of-sample results are in the [technical documentation](docs/dokumentacja.md).

## Data

The downloader uses yfinance to fetch the latest two years of daily Yahoo Finance data. It converts adjusted closing prices to USD using historical FX rates. It does not fill stock or ETF prices on market holidays. It also creates weekly observations from the last common trading session in each week.

The validated two-year snapshot from 2026-11-20 contains 485 common daily observations and 105 weekly prices (104 return intervals). The seven-year walk-forward dataset was downloaded and validated locally: 1,703 daily prices and 366 weekly prices for all 17 instruments, with no gaps in the weekly index and same-day FX availability. Price files and the audit report are local and ignored by Git. The reproducible download command is in the [technical documentation](docs/dokumentacja.md).

## Run

Python 3.10 or newer is required.

~~~bash
python -m pip install -r requirements.txt
python -m alpha221.market_data
python -m alpha221 --input data/prices_weekly_usd.csv --frequency weekly --risk-limit 0.22
~~~

The downloader writes adjusted daily USD prices to data/prices.csv, weekly prices to data/prices_weekly_usd.csv, latest closing prices to data/latest_prices_usd.csv, an audit to results/market_data_audit.csv, and a download manifest to data/market_data_manifest.json.

The comparison command runs the weekly optimizer with the project's 80/20 allocation, GA cardinality rule, and bootstrap probability objective. It uses the two-year input and is an in-sample estimate; use the seven-year walk-forward command in the technical documentation for out-of-sample evaluation. Weekly sampling annualizes with 52 periods; daily sampling uses 252:

~~~bash
python -m alpha221 --input data/prices.csv --frequency daily --risk-limit 0.22
~~~

Without an input file, python -m alpha221 uses synthetic demo prices.

## Project status

Data download, validation, currency conversion, weekly block-bootstrap probability estimation, target weight constraints, five-year walk-forward evaluation, and exhaustive evaluation of all 3,003 stock subsets are implemented. Allocation of an investment amount into asset units remains future work. See the [technical documentation](docs/dokumentacja.md) for results and limitations.

## Data source and limits

yfinance is an unofficial tool that uses Yahoo Finance's publicly available interfaces. This is an educational project, not an investment product. Yahoo places restrictions on data use and redistribution; downloaded price series are not published. See the [technical documentation](docs/dokumentacja.md).
