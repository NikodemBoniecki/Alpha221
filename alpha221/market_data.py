"""Download and validate the project's Yahoo Finance price data."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from .universe import ASSETS, ETFS as INDICES, STOCKS
FX_TICKERS = ["USDPLN=X", "EURUSD=X"]
QUOTE_CURRENCIES = {
    **dict.fromkeys(
        ["AAPL", "MSFT", "NVDA", "JPM", "KO", "TTWO", "AMD", "ASML", "TSLA", "SPY"],
        "USD",
    ),
    **dict.fromkeys(
        ["CDR.WA", "XTB.WA", "PKN.WA", "ASB.WA", "CBF.WA", "ETFBW20TR.WA"],
        "PLN",
    ),
    "UBI.PA": "EUR",
}
PLN_FX_TICKER = "USDPLN=X"
EUR_FX_TICKER = "EURUSD=X"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download adjusted asset prices, validate them, and normalize them to USD."
    )
    parser.add_argument(
        "--period", default="2y", help="Yahoo Finance history period (default: 2y; use 7y for walk-forward data)."
    )
    parser.add_argument(
        "--minimum-common-rows",
        type=int,
        default=450,
        help="Fail rather than silently use a shorter common history (default: 450).",
    )
    parser.add_argument("--prices-output", type=Path, default=Path("data/prices.csv"))
    parser.add_argument(
        "--weekly-output",
        type=Path,
        default=Path("data/prices_weekly_usd.csv"),
        help="Optional weekly snapshots using the last complete common session per week.",
    )
    parser.add_argument("--latest-output", type=Path, default=Path("data/latest_prices_usd.csv"))
    parser.add_argument("--audit-output", type=Path, default=Path("results/market_data_audit.csv"))
    parser.add_argument("--manifest-output", type=Path, default=Path("data/market_data_manifest.json"))
    return parser


def _extract_field(frame: pd.DataFrame, field: str) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        raise ValueError("Yahoo Finance returned columns in an unexpected format.")
    for level in range(frame.columns.nlevels):
        if field in frame.columns.get_level_values(level):
            extracted = frame.xs(field, axis=1, level=level, drop_level=True)
            if isinstance(extracted, pd.Series):
                extracted = extracted.to_frame()
            return extracted
    raise ValueError(f"Yahoo Finance did not return the required {field!r} field.")


def _fx_age_days(asset_dates: pd.DatetimeIndex, fx: pd.Series) -> int:
    available = fx.dropna().sort_index()
    if available.empty:
        raise ValueError("An FX series contains no usable observations.")
    positions = available.index.get_indexer(asset_dates, method="ffill")
    if np.any(positions < 0):
        raise ValueError("There is no previous FX observation for at least one asset date.")
    ages = asset_dates - available.index.take(positions)
    return int(max(age.days for age in ages))


def download_prices(
    period: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    tickers = ASSETS + FX_TICKERS
    raw = yf.download(
        tickers,
        period=period,
        interval="1d",
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=False,
    )
    if raw.empty:
        raise ValueError("Yahoo Finance returned no price data.")

    adjusted = _extract_field(raw, "Adj Close").sort_index()
    closes = _extract_field(raw, "Close").sort_index()
    if adjusted.index.has_duplicates or not adjusted.index.is_monotonic_increasing:
        raise ValueError("Yahoo Finance returned duplicate or unsorted dates.")

    missing_columns = [ticker for ticker in tickers if ticker not in adjusted.columns]
    if missing_columns:
        raise ValueError(f"No adjusted close column was returned for: {', '.join(missing_columns)}.")
    if any(ticker not in closes.columns for ticker in ASSETS + FX_TICKERS):
        raise ValueError("Yahoo Finance did not return close prices for every asset and FX ticker.")

    for ticker in tickers:
        observations = adjusted[ticker].dropna()
        if observations.empty:
            raise ValueError(f"No adjusted close observations were returned for {ticker}.")
        if not np.isfinite(observations.to_numpy()).all() or (observations <= 0).any():
            raise ValueError(f"Adjusted close values for {ticker} must be finite and positive.")

    usdpln = adjusted[PLN_FX_TICKER].dropna()
    eurusd = adjusted[EUR_FX_TICKER].dropna()
    if (usdpln <= 0).any() or (eurusd <= 0).any():
        raise ValueError("FX rates must be greater than zero.")

    # FX dates may differ from the local exchange calendar. Use only the most
    # recent rate on or before each price date; never fill asset price series.
    usdpln_on_index = usdpln.reindex(adjusted.index).ffill()
    eurusd_on_index = eurusd.reindex(adjusted.index).ffill()
    usd_prices = pd.DataFrame(index=adjusted.index)
    fx_ages: dict[str, int] = {}

    for ticker in ASSETS:
        local_prices = adjusted[ticker]
        currency = QUOTE_CURRENCIES[ticker]
        if currency == "PLN":
            fx_ages[ticker] = _fx_age_days(local_prices.dropna().index, usdpln)
            usd_prices[ticker] = local_prices / usdpln_on_index
        elif currency == "EUR":
            fx_ages[ticker] = _fx_age_days(local_prices.dropna().index, eurusd)
            usd_prices[ticker] = local_prices * eurusd_on_index
        else:
            usd_prices[ticker] = local_prices

    # Retain dates where every asset has an actual quote. No asset prices are
    # forward-filled, so closed-market dates cannot create artificial zero returns.
    common_prices = usd_prices.dropna(how="any")
    if common_prices.empty:
        raise ValueError("The selected assets do not have any common price dates.")
    if not np.isfinite(common_prices.to_numpy()).all() or (common_prices <= 0).any().any():
        raise ValueError("Converted USD prices must be finite and positive.")

    # One complete, same-date close per Friday-ending week. The row label is
    # the week-ending Friday; the value is the last common session in that week.
    weekly_prices = common_prices.resample("W-FRI").last().dropna(how="any")

    latest_rows = []
    audit_rows = []
    for ticker in ASSETS:
        local_close = closes[ticker].dropna()
        if local_close.empty:
            raise ValueError(f"No close prices were returned for {ticker}.")
        latest_date = local_close.index[-1]
        latest_close = float(local_close.iloc[-1])
        currency = QUOTE_CURRENCIES[ticker]
        fx_ticker = ""
        max_fx_age = 0
        if currency == "PLN":
            fx_ticker = PLN_FX_TICKER
            rate = usdpln_on_index.loc[latest_date]
            if pd.isna(rate):
                raise ValueError(f"No USD/PLN rate is available for {ticker}'s latest close.")
            latest_close /= float(rate)
        elif currency == "EUR":
            fx_ticker = EUR_FX_TICKER
            rate = eurusd_on_index.loc[latest_date]
            if pd.isna(rate):
                raise ValueError(f"No EUR/USD rate is available for {ticker}'s latest close.")
            latest_close *= float(rate)
        if ticker in fx_ages:
            max_fx_age = fx_ages[ticker]

        latest_rows.append(
            {"ticker": ticker, "date": latest_date.date().isoformat(), "close_usd": latest_close}
        )
        adjusted_observations = adjusted[ticker].dropna()
        audit_rows.append(
            {
                "ticker": ticker,
                "quote_currency": currency,
                "adjusted_close_observations": len(adjusted_observations),
                "first_observation": adjusted_observations.index[0].date().isoformat(),
                "last_observation": adjusted_observations.index[-1].date().isoformat(),
                "common_usd_observations": len(common_prices),
                "latest_close_date": latest_date.date().isoformat(),
                "latest_close_usd": latest_close,
                "fx_ticker": fx_ticker,
                "max_fx_age_days": max_fx_age,
            }
        )

    metadata: dict[str, object] = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "Yahoo Finance via yfinance",
        "yfinance_version": yf.__version__,
        "requested_period": period,
        "adjusted_price_field": "Adj Close",
        "latest_all_assets_close_field": "Close",
        "currency_conversions": {
            "PLN_to_USD": "PLN price / USDPLN=X (PLN per USD)",
            "EUR_to_USD": "EUR price * EURUSD=X (USD per EUR)",
            "FX_alignment": "most recent FX observation on or before the asset date",
        },
        "asset_tickers": ASSETS,
        "fx_tickers": FX_TICKERS,
        "common_observations": len(common_prices),
        "common_first_date": common_prices.index[0].date().isoformat(),
        "common_last_date": common_prices.index[-1].date().isoformat(),
        "weekly_observations": len(weekly_prices),
        "weekly_return_intervals": max(len(weekly_prices) - 1, 0),
        "weekly_sampling": "last complete common session in each Friday-ending week",
    }

    return (
        common_prices,
        weekly_prices,
        pd.DataFrame(latest_rows),
        pd.DataFrame(audit_rows),
        metadata,
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.minimum_common_rows < 3:
        parser.error("--minimum-common-rows must be at least 3.")

    try:
        prices, weekly, latest, audit, metadata = download_prices(args.period)
        if len(prices) < args.minimum_common_rows:
            raise ValueError(
                f"Only {len(prices)} complete common rows are available; "
                f"the configured minimum is {args.minimum_common_rows}. No ticker was dropped."
            )

        for path in [
            args.prices_output,
            args.weekly_output,
            args.latest_output,
            args.audit_output,
            args.manifest_output,
        ]:
            path.parent.mkdir(parents=True, exist_ok=True)

        prices.rename_axis("date").to_csv(args.prices_output, date_format="%Y-%m-%d", float_format="%.10g")
        weekly.rename_axis("date").to_csv(
            args.weekly_output,
            date_format="%Y-%m-%d",
            float_format="%.10g",
        )
        latest.to_csv(args.latest_output, index=False, float_format="%.10g")
        audit.to_csv(args.audit_output, index=False, float_format="%.10g")
        args.manifest_output.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        print(
            f"Validated {len(ASSETS)} assets and {len(FX_TICKERS)} FX series. "
            f"Saved {len(prices)} complete USD price rows "
            f"({metadata['common_first_date']} to {metadata['common_last_date']})."
        )
        print(f"Historical adjusted prices: {args.prices_output}")
        print(f"Weekly common-session prices: {args.weekly_output} ({len(weekly)} rows)")
        print(f"Latest unadjusted USD closes: {args.latest_output}")
        print(f"Validation report: {args.audit_output}")
        print(f"Data manifest: {args.manifest_output}")
    except (OSError, ValueError, KeyError, IndexError) as error:
        parser.exit(2, f"Data validation failed: {error}\n")


if __name__ == "__main__":
    main()
