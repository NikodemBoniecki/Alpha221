"""Download and audit the project's Yahoo Finance price data."""

import argparse
import hashlib
import json
import platform
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from .universe import ASSETS, ETFS, STOCKS


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
EXPECTED_INSTRUMENT_TYPES = {
    **dict.fromkeys(STOCKS, "EQUITY"),
    **dict.fromkeys(ETFS, "ETF"),
}
EXPECTED_TIMEZONES = {
    **dict.fromkeys(
        ["AAPL", "MSFT", "NVDA", "JPM", "KO", "TTWO", "AMD", "ASML", "TSLA", "SPY"],
        "America/New_York",
    ),
    **dict.fromkeys(
        ["CDR.WA", "XTB.WA", "PKN.WA", "ASB.WA", "CBF.WA", "ETFBW20TR.WA"],
        "Europe/Warsaw",
    ),
    "UBI.PA": "Europe/Paris",
}
EXPECTED_FX_METADATA = {
    "USDPLN=X": {"currency": "PLN", "instrument_type": "CURRENCY"},
    "EURUSD=X": {"currency": "USD", "instrument_type": "CURRENCY"},
}
PLN_FX_TICKER = "USDPLN=X"
EUR_FX_TICKER = "EURUSD=X"
DOWNLOAD_INTERVAL = "1d"
DEFAULT_MAX_FX_AGE_DAYS = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download, audit, and normalize adjusted asset prices to USD."
    )
    parser.add_argument(
        "--period",
        help="Relative Yahoo Finance history period. Defaults to 2y when start/end are omitted.",
    )
    parser.add_argument(
        "--start",
        help="Inclusive ISO start date for a reproducible fixed window (requires --end).",
    )
    parser.add_argument(
        "--end",
        help="Exclusive ISO end date for a reproducible fixed window (requires --start).",
    )
    parser.add_argument(
        "--minimum-common-rows",
        type=int,
        default=450,
        help="Fail rather than silently use a shorter common history (default: 450).",
    )
    parser.add_argument(
        "--max-fx-age-days",
        type=int,
        default=DEFAULT_MAX_FX_AGE_DAYS,
        help="Fail when a carried-forward FX observation is older than this many days (default: 4).",
    )
    parser.add_argument("--prices-output", type=Path, default=Path("data/prices.csv"))
    parser.add_argument(
        "--weekly-output",
        type=Path,
        default=Path("data/prices_weekly_usd.csv"),
        help="Weekly snapshots using the last complete common session per Friday-ending week.",
    )
    parser.add_argument("--latest-output", type=Path, default=Path("data/latest_prices_usd.csv"))
    parser.add_argument("--audit-output", type=Path, default=Path("results/market_data_audit.csv"))
    parser.add_argument(
        "--calendar-audit-output",
        type=Path,
        default=Path("results/market_data_calendar_audit.csv"),
        help="Week labels, actual source dates, and calendar lags.",
    )
    parser.add_argument("--manifest-output", type=Path, default=Path("data/market_data_manifest.json"))
    return parser


def _resolve_download_request(
    period: str | None,
    start: str | None,
    end: str | None,
) -> dict[str, object]:
    if period and (start or end):
        raise ValueError("Use either --period or the fixed --start/--end window, not both.")
    if bool(start) != bool(end):
        raise ValueError("--start and --end must be provided together.")

    if start and end:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
        except ValueError as error:
            raise ValueError("--start and --end must use ISO dates in YYYY-MM-DD format.") from error
        if start_date >= end_date:
            raise ValueError("--start must be earlier than the exclusive --end date.")
        return {
            "mode": "fixed",
            "start": start_date.isoformat(),
            "end_exclusive": end_date.isoformat(),
            "provider_query_start": (start_date - timedelta(days=1)).isoformat(),
            "provider_query_end_exclusive": (end_date + timedelta(days=1)).isoformat(),
            "provider_query_boundary_buffer_days": 1,
            "period": None,
            "reproducible_window": True,
        }

    return {
        "mode": "relative",
        "start": None,
        "end_exclusive": None,
        "provider_query_start": None,
        "provider_query_end_exclusive": None,
        "provider_query_boundary_buffer_days": 0,
        "period": period or "2y",
        "reproducible_window": False,
    }


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


def _extract_action_field(
    frame: pd.DataFrame,
    field: str,
    tickers: list[str],
) -> tuple[pd.DataFrame, bool]:
    try:
        extracted = _extract_field(frame, field)
    except ValueError:
        return pd.DataFrame(0.0, index=frame.index, columns=tickers), False
    return extracted.reindex(columns=tickers).fillna(0.0), True


def _provider_metadata(ticker: str) -> dict[str, str]:
    try:
        metadata = yf.Ticker(ticker).get_info()
    except Exception as error:
        raise ValueError(f"Could not retrieve provider metadata for {ticker}: {error}") from error
    if not isinstance(metadata, dict) or not metadata:
        raise ValueError(f"Yahoo Finance returned no provider metadata for {ticker}.")

    required = {
        "symbol": metadata.get("symbol"),
        "currency": metadata.get("currency"),
        "exchange": metadata.get("exchange"),
        "instrument_type": metadata.get("quoteType"),
        "timezone": metadata.get("exchangeTimezoneName"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"Provider metadata for {ticker} lacks: {', '.join(missing)}.")
    return {name: str(value) for name, value in required.items()}


def _verify_instrument_metadata(ticker: str) -> dict[str, object]:
    provider = _provider_metadata(ticker)
    expected_currency = QUOTE_CURRENCIES[ticker]
    expected_type = EXPECTED_INSTRUMENT_TYPES[ticker]
    expected_timezone = EXPECTED_TIMEZONES[ticker]
    symbol_matches = provider["symbol"].upper() == ticker.upper()
    currency_matches = provider["currency"].upper() == expected_currency
    type_matches = provider["instrument_type"].upper() == expected_type
    timezone_matches = provider["timezone"] == expected_timezone
    failures = []
    if not symbol_matches:
        failures.append(f"symbol={provider['symbol']!r}")
    if not currency_matches:
        failures.append(f"currency={provider['currency']!r}, expected {expected_currency!r}")
    if not type_matches:
        failures.append(f"type={provider['instrument_type']!r}, expected {expected_type!r}")
    if not timezone_matches:
        failures.append(f"timezone={provider['timezone']!r}, expected {expected_timezone!r}")
    if failures:
        raise ValueError(f"Provider metadata mismatch for {ticker}: {'; '.join(failures)}.")

    return {
        "provider_symbol": provider["symbol"],
        "provider_currency": provider["currency"].upper(),
        "provider_exchange": provider["exchange"],
        "provider_instrument_type": provider["instrument_type"].upper(),
        "provider_timezone": provider["timezone"],
        "symbol_matches": symbol_matches,
        "currency_matches": currency_matches,
        "instrument_type_matches": type_matches,
        "timezone_matches": timezone_matches,
    }


def _verify_fx_metadata(ticker: str) -> dict[str, str]:
    provider = _provider_metadata(ticker)
    expected = EXPECTED_FX_METADATA[ticker]
    failures = []
    if provider["symbol"].upper() != ticker.upper():
        failures.append(f"symbol={provider['symbol']!r}")
    if provider["currency"].upper() != expected["currency"]:
        failures.append(f"currency={provider['currency']!r}, expected {expected['currency']!r}")
    if provider["instrument_type"].upper() != expected["instrument_type"]:
        failures.append(
            f"type={provider['instrument_type']!r}, expected {expected['instrument_type']!r}"
        )
    if failures:
        raise ValueError(f"Provider metadata mismatch for {ticker}: {'; '.join(failures)}.")
    return provider


def _align_fx(
    asset_dates: pd.DatetimeIndex,
    fx: pd.Series,
) -> tuple[pd.Series, dict[str, object]]:
    available = fx.dropna().sort_index()
    if available.empty:
        raise ValueError("An FX series contains no usable observations.")
    positions = available.index.get_indexer(asset_dates, method="ffill")
    if np.any(positions < 0):
        raise ValueError("There is no previous FX observation for at least one asset date.")

    matched_dates = available.index.take(positions)
    ages = np.asarray([(asset_date - fx_date).days for asset_date, fx_date in zip(asset_dates, matched_dates)])
    if np.any(ages < 0):
        raise ValueError("FX alignment used a future observation.")
    aligned = pd.Series(available.iloc[positions].to_numpy(), index=asset_dates, dtype=float)
    return aligned, {
        "fx_observations": len(asset_dates),
        "fx_exact_date_observations": int(np.sum(ages == 0)),
        "fx_carried_forward_observations": int(np.sum(ages > 0)),
        "fx_max_age_days": int(np.max(ages)) if len(ages) else 0,
        "fx_mean_age_days": float(np.mean(ages)) if len(ages) else 0.0,
    }


def _corporate_action_stats(
    ticker: str,
    closes: pd.DataFrame,
    adjusted: pd.DataFrame,
    dividends: pd.DataFrame,
    splits: pd.DataFrame,
) -> dict[str, object]:
    paired = pd.concat(
        [closes[ticker].rename("close"), adjusted[ticker].rename("adjusted")],
        axis=1,
    ).dropna()
    if paired.empty:
        raise ValueError(f"No overlapping Close and Adj Close values were returned for {ticker}.")
    if not np.isfinite(paired.to_numpy()).all() or (paired <= 0).any().any():
        raise ValueError(f"Close and Adj Close values for {ticker} must be finite and positive.")

    factors = paired["adjusted"] / paired["close"]
    factor_changes = factors.pct_change().dropna()
    return {
        "dividend_events": int((dividends[ticker] != 0).sum()),
        "split_events": int((splits[ticker] != 0).sum()),
        "adjusted_differs_from_close": int((~np.isclose(factors, 1.0, rtol=1e-9, atol=1e-12)).sum()),
        "adjustment_factor_change_points": int(
            (~np.isclose(factor_changes, 0.0, rtol=0.0, atol=1e-6)).sum()
        ),
        "adjustment_factor_min": float(factors.min()),
        "adjustment_factor_max": float(factors.max()),
        "adjustment_factor_first": float(factors.iloc[0]),
        "adjustment_factor_last": float(factors.iloc[-1]),
    }


def _weekly_snapshots(common_prices: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    weekly_prices = common_prices.resample("W-FRI").last().dropna(how="any")
    source_dates = (
        pd.Series(common_prices.index, index=common_prices.index)
        .resample("W-FRI")
        .last()
        .reindex(weekly_prices.index)
    )
    if weekly_prices.empty or source_dates.isna().any():
        raise ValueError("Could not construct complete weekly snapshots.")

    expected_weeks = pd.date_range(weekly_prices.index[0], weekly_prices.index[-1], freq="W-FRI")
    missing_weeks = expected_weeks.difference(weekly_prices.index)
    if len(missing_weeks):
        formatted = ", ".join(item.date().isoformat() for item in missing_weeks[:5])
        raise ValueError(f"Weekly data contain missing Friday-ending weeks: {formatted}.")

    lags = (weekly_prices.index - pd.DatetimeIndex(source_dates)).days
    if np.any(lags < 0) or np.any(lags > 6):
        raise ValueError("A weekly snapshot uses an invalid source date.")
    calendar_audit = pd.DataFrame(
        {
            "week_ending": weekly_prices.index.date.astype(str),
            "source_date": pd.DatetimeIndex(source_dates).date.astype(str),
            "days_before_friday": lags,
            "source_is_friday": lags == 0,
        }
    )
    return weekly_prices, calendar_audit


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_prices(
    period: str | None = None,
    start: str | None = None,
    end: str | None = None,
    max_fx_age_days: int = DEFAULT_MAX_FX_AGE_DAYS,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, object],
]:
    if max_fx_age_days < 0:
        raise ValueError("max_fx_age_days cannot be negative.")
    if (
        set(QUOTE_CURRENCIES) != set(ASSETS)
        or set(EXPECTED_INSTRUMENT_TYPES) != set(ASSETS)
        or set(EXPECTED_TIMEZONES) != set(ASSETS)
    ):
        raise ValueError("The instrument audit registry must cover the exact project universe.")

    request = _resolve_download_request(period, start, end)
    tickers = ASSETS + FX_TICKERS
    download_arguments: dict[str, object] = {
        "tickers": tickers,
        "interval": DOWNLOAD_INTERVAL,
        "auto_adjust": False,
        "actions": True,
        "repair": False,
        "progress": False,
        "threads": False,
    }
    if request["mode"] == "fixed":
        download_arguments["start"] = request["provider_query_start"]
        download_arguments["end"] = request["provider_query_end_exclusive"]
    else:
        download_arguments["period"] = request["period"]

    raw = yf.download(**download_arguments)
    if raw.empty:
        raise ValueError("Yahoo Finance returned no price data.")
    if request["mode"] == "fixed":
        start_date = date.fromisoformat(str(request["start"]))
        end_date = date.fromisoformat(str(request["end_exclusive"]))
        requested_rows = np.fromiter(
            (start_date <= timestamp.date() < end_date for timestamp in raw.index),
            dtype=bool,
            count=len(raw.index),
        )
        raw = raw.loc[requested_rows]
        if raw.empty:
            raise ValueError("Yahoo Finance returned no observations inside the fixed date window.")

    adjusted = _extract_field(raw, "Adj Close").sort_index()
    closes = _extract_field(raw, "Close").sort_index()
    dividends, dividend_field_returned = _extract_action_field(raw, "Dividends", ASSETS)
    splits, split_field_returned = _extract_action_field(raw, "Stock Splits", ASSETS)
    if not dividend_field_returned or not split_field_returned:
        raise ValueError(
            "Yahoo Finance did not return both Dividends and Stock Splits fields; "
            "corporate-action auditing cannot continue."
        )
    if adjusted.index.has_duplicates or not adjusted.index.is_monotonic_increasing:
        raise ValueError("Yahoo Finance returned duplicate or unsorted dates.")

    missing_columns = [ticker for ticker in tickers if ticker not in adjusted.columns]
    if missing_columns:
        raise ValueError(f"No adjusted close column was returned for: {', '.join(missing_columns)}.")
    if any(ticker not in closes.columns for ticker in tickers):
        raise ValueError("Yahoo Finance did not return close prices for every asset and FX ticker.")

    for ticker in tickers:
        observations = adjusted[ticker].dropna()
        if observations.empty:
            raise ValueError(f"No adjusted close observations were returned for {ticker}.")
        if not np.isfinite(observations.to_numpy()).all() or (observations <= 0).any():
            raise ValueError(f"Adjusted close values for {ticker} must be finite and positive.")

    provider_metadata = {ticker: _verify_instrument_metadata(ticker) for ticker in ASSETS}
    fx_provider_metadata = {ticker: _verify_fx_metadata(ticker) for ticker in FX_TICKERS}
    action_stats = {
        ticker: _corporate_action_stats(ticker, closes, adjusted, dividends, splits)
        for ticker in ASSETS
    }

    usdpln = adjusted[PLN_FX_TICKER].dropna()
    eurusd = adjusted[EUR_FX_TICKER].dropna()
    if (usdpln <= 0).any() or (eurusd <= 0).any():
        raise ValueError("FX rates must be greater than zero.")

    usd_prices = pd.DataFrame(index=adjusted.index)
    fx_stats: dict[str, dict[str, object]] = {}
    for ticker in ASSETS:
        local_prices = adjusted[ticker]
        actual_prices = local_prices.dropna()
        currency = QUOTE_CURRENCIES[ticker]
        if currency == "PLN":
            aligned_fx, fx_stats[ticker] = _align_fx(actual_prices.index, usdpln)
            usd_prices.loc[actual_prices.index, ticker] = actual_prices / aligned_fx
        elif currency == "EUR":
            aligned_fx, fx_stats[ticker] = _align_fx(actual_prices.index, eurusd)
            usd_prices.loc[actual_prices.index, ticker] = actual_prices * aligned_fx
        else:
            usd_prices.loc[actual_prices.index, ticker] = actual_prices
            fx_stats[ticker] = {
                "fx_observations": 0,
                "fx_exact_date_observations": 0,
                "fx_carried_forward_observations": 0,
                "fx_max_age_days": 0,
                "fx_mean_age_days": 0.0,
            }
        if int(fx_stats[ticker]["fx_max_age_days"]) > max_fx_age_days:
            raise ValueError(
                f"{ticker} used an FX observation {fx_stats[ticker]['fx_max_age_days']} days old; "
                f"the configured maximum is {max_fx_age_days}."
            )

    common_prices = usd_prices.dropna(how="any")
    if common_prices.empty:
        raise ValueError("The selected assets do not have any common price dates.")
    if not np.isfinite(common_prices.to_numpy()).all() or (common_prices <= 0).any().any():
        raise ValueError("Converted USD prices must be finite and positive.")

    weekly_prices, calendar_audit = _weekly_snapshots(common_prices)
    union_asset_dates = adjusted[ASSETS].dropna(how="all").index

    latest_rows = []
    audit_rows = []
    for ticker in ASSETS:
        local_close = closes[ticker].dropna()
        if local_close.empty:
            raise ValueError(f"No close prices were returned for {ticker}.")
        latest_date = local_close.index[-1]
        latest_close = float(local_close.iloc[-1])
        if not np.isfinite(latest_close) or latest_close <= 0:
            raise ValueError(f"Latest Close for {ticker} must be finite and positive.")
        currency = QUOTE_CURRENCIES[ticker]
        fx_ticker = ""
        latest_fx_age_days = 0
        if currency == "PLN":
            fx_ticker = PLN_FX_TICKER
            aligned, latest_stats = _align_fx(pd.DatetimeIndex([latest_date]), usdpln)
            latest_close /= float(aligned.iloc[0])
            latest_fx_age_days = int(latest_stats["fx_max_age_days"])
        elif currency == "EUR":
            fx_ticker = EUR_FX_TICKER
            aligned, latest_stats = _align_fx(pd.DatetimeIndex([latest_date]), eurusd)
            latest_close *= float(aligned.iloc[0])
            latest_fx_age_days = int(latest_stats["fx_max_age_days"])
        if latest_fx_age_days > max_fx_age_days:
            raise ValueError(
                f"{ticker}'s latest Close used an FX observation {latest_fx_age_days} days old; "
                f"the configured maximum is {max_fx_age_days}."
            )
        if not np.isfinite(latest_close) or latest_close <= 0:
            raise ValueError(f"Latest USD Close for {ticker} must be finite and positive.")

        latest_rows.append(
            {"ticker": ticker, "date": latest_date.date().isoformat(), "close_usd": latest_close}
        )
        observations = adjusted[ticker].dropna()
        audit_rows.append(
            {
                "ticker": ticker,
                "audit_status": "PASS",
                "expected_currency": currency,
                "expected_instrument_type": EXPECTED_INSTRUMENT_TYPES[ticker],
                **provider_metadata[ticker],
                "adjusted_close_observations": len(observations),
                "first_observation": observations.index[0].date().isoformat(),
                "last_observation": observations.index[-1].date().isoformat(),
                "union_calendar_observations": len(union_asset_dates),
                "missing_on_union_calendar": int(len(union_asset_dates.difference(observations.index))),
                "common_usd_observations": len(common_prices),
                "observations_removed_by_common_calendar": int(len(observations) - len(common_prices)),
                **action_stats[ticker],
                "latest_close_date": latest_date.date().isoformat(),
                "latest_close_usd": latest_close,
                "fx_ticker": fx_ticker,
                **fx_stats[ticker],
                "latest_fx_age_days": latest_fx_age_days,
            }
        )

    metadata: dict[str, object] = {
        "manifest_schema_version": 2,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "Yahoo Finance via yfinance",
        "request": {
            **request,
            "interval": DOWNLOAD_INTERVAL,
            "auto_adjust": False,
            "actions": True,
            "repair": False,
            "threads": False,
            "maximum_fx_age_days": max_fx_age_days,
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "yfinance": yf.__version__,
            "market_data_module_sha256": _sha256_file(Path(__file__)),
        },
        "adjusted_price_field": "Adj Close",
        "latest_all_assets_close_field": "Close",
        "corporate_action_fields": {
            "dividends_returned": dividend_field_returned,
            "stock_splits_returned": split_field_returned,
        },
        "currency_conversions": {
            "PLN_to_USD": "PLN price / USDPLN=X (PLN per USD)",
            "EUR_to_USD": "EUR price * EURUSD=X (USD per EUR)",
            "FX_alignment": "most recent FX observation on or before the asset date",
        },
        "asset_tickers": ASSETS,
        "fx_tickers": FX_TICKERS,
        "fx_provider_metadata": fx_provider_metadata,
        "common_observations": len(common_prices),
        "common_first_date": common_prices.index[0].date().isoformat(),
        "common_last_date": common_prices.index[-1].date().isoformat(),
        "weekly_observations": len(weekly_prices),
        "weekly_return_intervals": max(len(weekly_prices) - 1, 0),
        "weekly_sampling": "last complete common session in each Friday-ending week",
        "weekly_source_date_audit": {
            "source_on_friday": int(calendar_audit["source_is_friday"].sum()),
            "source_before_friday": int((~calendar_audit["source_is_friday"]).sum()),
            "maximum_days_before_friday": int(calendar_audit["days_before_friday"].max()),
        },
    }
    return (
        common_prices,
        weekly_prices,
        pd.DataFrame(latest_rows),
        pd.DataFrame(audit_rows),
        calendar_audit,
        metadata,
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.minimum_common_rows < 3:
        parser.error("--minimum-common-rows must be at least 3.")
    if args.max_fx_age_days < 0:
        parser.error("--max-fx-age-days cannot be negative.")

    try:
        prices, weekly, latest, audit, calendar_audit, metadata = download_prices(
            period=args.period,
            start=args.start,
            end=args.end,
            max_fx_age_days=args.max_fx_age_days,
        )
        if len(prices) < args.minimum_common_rows:
            raise ValueError(
                f"Only {len(prices)} complete common rows are available; "
                f"the configured minimum is {args.minimum_common_rows}. No ticker was dropped."
            )

        output_paths = {
            "daily_prices": args.prices_output,
            "weekly_prices": args.weekly_output,
            "latest_prices": args.latest_output,
            "instrument_audit": args.audit_output,
            "calendar_audit": args.calendar_audit_output,
        }
        output_frames = {
            "daily_prices": prices,
            "weekly_prices": weekly,
            "latest_prices": latest,
            "instrument_audit": audit,
            "calendar_audit": calendar_audit,
        }
        for path in [*output_paths.values(), args.manifest_output]:
            path.parent.mkdir(parents=True, exist_ok=True)

        prices.rename_axis("date").to_csv(
            args.prices_output, date_format="%Y-%m-%d", float_format="%.10g"
        )
        weekly.rename_axis("date").to_csv(
            args.weekly_output,
            date_format="%Y-%m-%d",
            float_format="%.10g",
        )
        latest.to_csv(args.latest_output, index=False, float_format="%.10g")
        audit.to_csv(args.audit_output, index=False, float_format="%.10g")
        calendar_audit.to_csv(args.calendar_audit_output, index=False)

        metadata["outputs"] = {
            name: {
                "path": str(path),
                "sha256": _sha256_file(path),
                "rows": len(output_frames[name]),
                "columns": [str(column) for column in output_frames[name].columns],
            }
            for name, path in output_paths.items()
        }
        args.manifest_output.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(
            f"Audited {len(ASSETS)} assets and {len(FX_TICKERS)} FX series. "
            f"Saved {len(prices)} complete USD price rows "
            f"({metadata['common_first_date']} to {metadata['common_last_date']})."
        )
        print(f"Historical adjusted prices: {args.prices_output}")
        print(f"Weekly common-session prices: {args.weekly_output} ({len(weekly)} rows)")
        print(f"Latest unadjusted USD closes: {args.latest_output}")
        print(f"Instrument, action, and FX audit: {args.audit_output}")
        print(f"Calendar audit: {args.calendar_audit_output}")
        print(f"Reproducibility manifest: {args.manifest_output}")
    except (OSError, ValueError, KeyError, IndexError) as error:
        parser.exit(2, f"Data audit failed: {error}\n")


if __name__ == "__main__":
    main()
