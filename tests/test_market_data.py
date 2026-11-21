import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from alpha221.market_data import (
    _align_fx,
    _corporate_action_stats,
    _resolve_download_request,
    _verify_instrument_metadata,
    _weekly_snapshots,
)


class DownloadRequestTests(unittest.TestCase):
    def test_defaults_to_relative_two_year_window(self) -> None:
        request = _resolve_download_request(None, None, None)

        self.assertEqual(request["mode"], "relative")
        self.assertEqual(request["period"], "2y")
        self.assertFalse(request["reproducible_window"])

    def test_fixed_window_is_marked_reproducible(self) -> None:
        request = _resolve_download_request(None, "2019-11-21", "2026-11-21")

        self.assertEqual(request["mode"], "fixed")
        self.assertEqual(request["end_exclusive"], "2026-11-21")
        self.assertEqual(request["provider_query_start"], "2019-11-20")
        self.assertEqual(request["provider_query_end_exclusive"], "2026-11-22")
        self.assertTrue(request["reproducible_window"])

    def test_rejects_mixed_relative_and_fixed_window(self) -> None:
        with self.assertRaises(ValueError):
            _resolve_download_request("7y", "2019-11-21", "2026-11-21")


class MetadataAuditTests(unittest.TestCase):
    @patch("alpha221.market_data._provider_metadata")
    def test_accepts_matching_provider_metadata(self, provider_metadata) -> None:
        provider_metadata.return_value = {
            "symbol": "AAPL",
            "currency": "USD",
            "exchange": "NMS",
            "instrument_type": "EQUITY",
            "timezone": "America/New_York",
        }

        result = _verify_instrument_metadata("AAPL")

        self.assertTrue(result["symbol_matches"])
        self.assertTrue(result["currency_matches"])
        self.assertTrue(result["timezone_matches"])

    @patch("alpha221.market_data._provider_metadata")
    def test_rejects_wrong_provider_currency(self, provider_metadata) -> None:
        provider_metadata.return_value = {
            "symbol": "AAPL",
            "currency": "EUR",
            "exchange": "NMS",
            "instrument_type": "EQUITY",
            "timezone": "America/New_York",
        }

        with self.assertRaisesRegex(ValueError, "currency"):
            _verify_instrument_metadata("AAPL")


class FxAuditTests(unittest.TestCase):
    def test_reports_exact_and_carried_forward_rates(self) -> None:
        fx = pd.Series(
            [4.0, 4.1],
            index=pd.to_datetime(["2026-01-05", "2026-01-07"]),
        )
        asset_dates = pd.DatetimeIndex(
            pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
        )

        aligned, stats = _align_fx(asset_dates, fx)

        np.testing.assert_allclose(aligned.to_numpy(), [4.0, 4.0, 4.1])
        self.assertEqual(stats["fx_exact_date_observations"], 2)
        self.assertEqual(stats["fx_carried_forward_observations"], 1)
        self.assertEqual(stats["fx_max_age_days"], 1)

    def test_rejects_when_only_future_rate_exists(self) -> None:
        fx = pd.Series([4.0], index=pd.to_datetime(["2026-01-06"]))

        with self.assertRaisesRegex(ValueError, "previous FX observation"):
            _align_fx(pd.DatetimeIndex(pd.to_datetime(["2026-01-05"])), fx)


class CorporateActionAuditTests(unittest.TestCase):
    def test_counts_events_and_adjustment_changes(self) -> None:
        index = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
        closes = pd.DataFrame({"TEST": [100.0, 98.0, 50.0]}, index=index)
        adjusted = pd.DataFrame({"TEST": [90.0, 90.0, 50.0]}, index=index)
        dividends = pd.DataFrame({"TEST": [0.0, 2.0, 0.0]}, index=index)
        splits = pd.DataFrame({"TEST": [0.0, 0.0, 2.0]}, index=index)

        stats = _corporate_action_stats("TEST", closes, adjusted, dividends, splits)

        self.assertEqual(stats["dividend_events"], 1)
        self.assertEqual(stats["split_events"], 1)
        self.assertEqual(stats["adjustment_factor_change_points"], 2)


class CalendarAuditTests(unittest.TestCase):
    def test_preserves_actual_source_date_for_each_week(self) -> None:
        index = pd.to_datetime(["2026-01-02", "2026-01-08"])
        prices = pd.DataFrame({"A": [10.0, 11.0], "B": [20.0, 21.0]}, index=index)

        weekly, audit = _weekly_snapshots(prices)

        self.assertEqual(len(weekly), 2)
        self.assertEqual(audit.loc[0, "days_before_friday"], 0)
        self.assertEqual(audit.loc[1, "days_before_friday"], 1)
        self.assertFalse(bool(audit.loc[1, "source_is_friday"]))


if __name__ == "__main__":
    unittest.main()
