# Alpha221: Genetic Algorithm for Portfolio Optimization

AI course project at Collegium Da Vinci, Computer Science, group L2 / L3, academic year 2026/2027.

[Polska wersja README](README_PL.md) | [Project card](karta-tematu.md) | [English project card](project_card_en.md)

## What it does

The program helps individual investors compare ways to divide money among selected stocks. It reads historical daily prices and a risk limit, then suggests portfolio weights and estimates return and risk. It can use a local CSV file or synthetic demo prices. We selected a [CC0 dataset of daily U.S. stock prices](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs), but have not downloaded it yet.

## AI technique

The program uses a genetic algorithm to search possible portfolio weights under a risk limit. It compares the result with a Markowitz optimizer and a simple equal-weight portfolio. The current Python skeleton has the main algorithm and both baselines.

## Results

We have not evaluated the algorithm on licensed market data yet. Our target is for every returned portfolio to meet the risk limit and for median return to reach at least 95% of the Markowitz result across five test cases. The built-in synthetic demo is for trying the program, not for reporting project results.

## How to run

Requirements: Python 3.10 or newer.

```bash
git clone https://github.com/NikodemBoniecki/Alpha221.git
cd Alpha221
python -m pip install -r requirements.txt
python -m alpha221
```

The default command generates synthetic prices and writes a comparison to `results/comparison.csv`. To use a CSV file, run `python -m alpha221 --input data/prices.csv --risk-limit 0.25`. The CSV must have a `date` column followed by one closing price column per ticker. We plan to prepare that file from five Kaggle ticker files. See [our Tiingo licensing notes](docs/tiingo-data-notes.md).

## Team

- Kacper Nowaczyk: genetic algorithm design and operators.
- Adam Remfeld: choosing a licensed data source, acquiring and preparing data.
- Nikodem Boniecki: baselines, evaluation, integration, and documentation.

## Documentation

Read the [full documentation in Polish](docs/dokumentacja.md), the [technical abstract in English](docs/abstract_en.md), and [our notes on Tiingo data](docs/tiingo-data-notes.md).
