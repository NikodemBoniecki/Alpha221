# Alpha221: Genetic Algorithm for Portfolio Optimization

AI course project at Collegium Da Vinci, Computer Science, group L2 / L3, academic year 2026/2027.

[Polska wersja README](README_PL.md) | [Project card](karta-tematu.md) | [English project card](project_card_en.md)

## What it does

We plan to build a tool that helps individual investors divide money among selected stocks. It will use historical daily prices and a risk limit to suggest portfolio weights, then show the portfolio's estimated return and risk. We will start with companies from AI, game development, and semiconductor sectors.

## AI technique

We chose a genetic algorithm and will implement its main parts ourselves. It can search many possible portfolio weights while taking the user's risk limit into account. We will compare its results with a Markowitz optimizer and a simple equal-weight portfolio.

## Results

We have not run the experiments yet because the implementation has not started. Our initial target is for every returned portfolio to meet the risk limit and for median return to reach at least 95% of the Markowitz result across five test cases.

## How to run

There is no runnable code in the repository yet. We will add the Python version, dependencies, data setup, run command, and output location when we add the project skeleton. Tiingo EOD is only a possible data source: Starter and Trial plans do not allow persistent data storage, and our planned AI comparison requires an Enterprise license. We will secure that license or choose a suitably licensed dataset before downloading data. See [our Tiingo research](docs/tiingo-data-notes.md).

## Team

- Kacper Nowaczyk: genetic algorithm design and operators.
- Adam Remfeld: choosing a licensed data source, acquiring and preparing data.
- Nikodem Boniecki: baselines, evaluation, integration, and documentation.

## Documentation

Read the [full documentation in Polish](docs/dokumentacja.md), the [technical abstract in English](docs/abstract_en.md), and [our notes on Tiingo data](docs/tiingo-data-notes.md).
