# Alpha221: Genetic Algorithm for Risk-Constrained Portfolio Optimization

Alpha221 is a planned course project that explores portfolio construction for retail investors. Given historical daily prices for a selected set of stocks and a user-defined risk limit, the system will search for non-negative portfolio weights that sum to one and maximize estimated return while satisfying the risk constraint. The initial stock universe is expected to focus on AI, game development, and semiconductor companies.

The project will implement a genetic algorithm from scratch, including population initialization, selection, crossover, mutation, and fitness evaluation. Portfolio returns and covariance will be calculated from historical daily returns. The genetic algorithm will be compared on the same test periods with an equal-weight portfolio and a Markowitz mean-variance optimizer. A provisional target is for every returned portfolio to satisfy the risk limit and for median expected return to reach at least 95% of the Markowitz result across five test cases.

The project is still at the planning stage. The ticker universe, dates, final parameters, implementation, and empirical results remain to be determined. The intended implementation will run on CPU and will use Tiingo EOD data if access and usage terms are confirmed. The prototype is educational and is not an investment recommendation.
