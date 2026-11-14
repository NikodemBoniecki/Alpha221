# Alpha221: Genetic Algorithm for Risk-Constrained Portfolio Optimization

We are building a course project that helps individual investors choose how to divide money among selected stocks. The program will use historical daily prices and a risk limit to suggest portfolio weights and estimate return and risk. We will start with companies from AI, game development, and semiconductor sectors.

The program uses a genetic algorithm with population initialization, selection, crossover, mutation, and fitness evaluation. It calculates returns and covariance from daily price changes, then compares the result with an equal-weight portfolio and a Markowitz optimizer. Our initial target is for every returned portfolio to meet the risk limit and for median return to reach at least 95% of the Markowitz result across five test cases.

The runnable Python skeleton is in place. It can generate synthetic prices for a demo or read prices from a local CSV file, then save a comparison to `results/comparison.csv`. We selected the CC0 [Huge Stock Market Dataset](https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs), but have not downloaded or evaluated it yet. We plan to use five tickers from 2012 to 2017. The demo is not a project result. The program runs on CPU and is a course project, not investment advice.
