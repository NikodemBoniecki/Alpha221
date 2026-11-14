# Alpha221: Genetic Algorithm for Risk-Constrained Portfolio Optimization

We are building a course project that helps individual investors choose how to divide money among selected stocks. The program will use historical daily prices and a risk limit to suggest portfolio weights and estimate return and risk. We will start with companies from AI, game development, and semiconductor sectors.

The program uses a genetic algorithm with population initialization, selection, crossover, mutation, and fitness evaluation. It calculates returns and covariance from daily price changes, then compares the result with an equal-weight portfolio and a Markowitz optimizer. Our initial target is for every returned portfolio to meet the risk limit and for median return to reach at least 95% of the Markowitz result across five test cases.

The runnable Python skeleton is in place. It can generate synthetic prices for a demo or read prices from a local CSV file, then save a comparison to `results/comparison.csv`. We have not selected a licensed market dataset or run experiments on real prices yet, so the demo is not a project result. We will use Tiingo EOD only if a license allows storage and AI evaluation; otherwise, we will choose a dataset with suitable terms. The program runs on CPU and is a course project, not investment advice.
