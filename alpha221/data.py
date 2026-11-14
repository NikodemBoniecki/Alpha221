import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np


def load_prices(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        rows = list(reader)

    if header is None or len(header) < 3 or header[0].strip().lower() != "date":
        raise ValueError("CSV needs a date column followed by at least two ticker columns.")

    tickers = [value.strip() for value in header[1:]]
    if any(not ticker for ticker in tickers) or len(set(tickers)) != len(tickers):
        raise ValueError("Ticker names must be present and unique.")
    if len(rows) < 3:
        raise ValueError("CSV needs at least three rows of prices.")

    dates: list[date] = []
    prices: list[list[float]] = []

    for line_number, row in enumerate(rows, start=2):
        if len(row) != len(header):
            raise ValueError(f"Row {line_number} has {len(row)} columns; expected {len(header)}.")

        try:
            row_date = date.fromisoformat(row[0].strip())
            row_prices = [float(value) for value in row[1:]]
        except ValueError as error:
            raise ValueError(f"Invalid date or price on row {line_number}.") from error

        if not all(np.isfinite(value) and value > 0 for value in row_prices):
            raise ValueError(f"Prices on row {line_number} must be finite and greater than zero.")
        dates.append(row_date)
        prices.append(row_prices)

    if dates != sorted(set(dates)):
        raise ValueError("Dates must be unique and sorted from oldest to newest.")

    return tickers, np.asarray(prices, dtype=float)


def make_demo_prices(seed: int = 7, periods: int = 252) -> tuple[list[str], list[str], np.ndarray]:
    tickers = ["AI_A", "CHIP_A", "CHIP_B", "GAME_A", "GAME_B"]
    rng = np.random.default_rng(seed)

    market_returns = rng.normal(0.0002, 0.008, size=(periods, 1))
    betas = np.array([1.0, 1.2, 0.9, 1.1, 0.8])
    daily_drift = np.array([0.0005, 0.0006, 0.00035, 0.00055, 0.0004])
    noise = rng.normal(0, 0.006, size=(periods, len(tickers)))
    returns = daily_drift + market_returns * betas + noise
    prices = np.vstack((np.full(len(tickers), 100.0), 100.0 * np.cumprod(1 + returns, axis=0)))

    dates: list[str] = []
    current = date(2024, 1, 2)
    while len(dates) < periods + 1:
        if current.weekday() < 5:
            dates.append(current.isoformat())
        current += timedelta(days=1)

    return tickers, dates, prices


def calculate_returns(prices: np.ndarray) -> np.ndarray:
    if prices.ndim != 2 or prices.shape[0] < 3 or prices.shape[1] < 2:
        raise ValueError("Prices must contain at least three dates and two tickers.")
    if not np.all(np.isfinite(prices)) or np.any(prices <= 0):
        raise ValueError("Prices must be finite and greater than zero.")
    return prices[1:] / prices[:-1] - 1.0
