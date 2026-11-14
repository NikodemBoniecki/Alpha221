import argparse
import csv
import math
from datetime import date
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a wide price CSV from per-ticker Kaggle files.")
    parser.add_argument("--source", type=Path, required=True, help="Folder containing the Kaggle stock files.")
    parser.add_argument("--tickers", nargs="+", required=True, help="Ticker symbols to include.")
    parser.add_argument("--start", type=date.fromisoformat, required=True, help="First date in YYYY-MM-DD format.")
    parser.add_argument("--end", type=date.fromisoformat, required=True, help="Last date in YYYY-MM-DD format.")
    parser.add_argument("--output", type=Path, default=Path("data/prices.csv"), help="Where to save the wide CSV.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("--start must be on or before --end.")
    if not args.source.is_dir():
        parser.error(f"Source folder does not exist: {args.source}")

    try:
        tickers = [ticker.upper() for ticker in args.tickers]
        if len(tickers) < 2 or len(set(tickers)) != len(tickers):
            parser.error("Provide at least two unique ticker symbols.")
        series = {ticker: _load_ticker(args.source, ticker, args.start, args.end) for ticker in tickers}
        common_dates = sorted(set.intersection(*(set(values) for values in series.values())))
        if len(common_dates) < 3:
            raise ValueError("The selected tickers have fewer than three shared dates in this range.")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["date", *tickers])
            for item in common_dates:
                writer.writerow([item.isoformat(), *(series[ticker][item] for ticker in tickers)])

        print(f"Prepared {len(common_dates)} common dates for {len(tickers)} tickers.")
        print(f"Saved prices to {args.output}.")
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")


def _load_ticker(source: Path, ticker: str, start: date, end: date) -> dict[date, float]:
    path = _find_ticker_file(source, ticker)
    if path is None:
        raise ValueError(f"Could not find a data file for ticker {ticker} in {source}.")

    with path.open(newline="", encoding="utf-8-sig") as file:
        sample = file.read(4096)
        file.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(file, dialect=dialect)
        columns = {name.strip().lower(): name for name in reader.fieldnames or []}
        if "date" not in columns or "close" not in columns:
            raise ValueError(f"{path} must contain Date and Close columns.")

        prices: dict[date, float] = {}
        for line_number, row in enumerate(reader, start=2):
            try:
                item = date.fromisoformat(row[columns["date"]].strip())
                close = float(row[columns["close"]])
            except (AttributeError, ValueError, TypeError) as error:
                raise ValueError(f"Invalid date or closing price in {path} on row {line_number}.") from error
            if start <= item <= end:
                if not math.isfinite(close) or close <= 0:
                    raise ValueError(f"Closing price must be finite and positive in {path} on row {line_number}.")
                if item in prices:
                    raise ValueError(f"Duplicate date {item} in {path}.")
                prices[item] = close

    if not prices:
        raise ValueError(f"No prices for ticker {ticker} between {start} and {end}.")
    return prices


def _find_ticker_file(source: Path, ticker: str) -> Path | None:
    matches = [
        path
        for path in source.rglob("*")
        if path.is_file() and path.name.lower().split(".")[0] == ticker.lower()
    ]
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"Found more than one data file for ticker {ticker}: {matches}")
    return matches[0]


if __name__ == "__main__":
    main()
