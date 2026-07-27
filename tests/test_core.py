from __future__ import annotations
import unittest
from datetime import datetime, timezone
from core.chart import calculate_chart
from core.timezone import resolve_local_time

class CoreChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = calculate_chart(datetime(1990, 1, 1, 4, 0, tzinfo=timezone.utc), 22.9999, 120.2270, datetime(2026, 7, 27, tzinfo=timezone.utc))

    def test_expected_charts_exist(self):
        self.assertEqual(set(self.result["charts"]), {"D1", "Moon", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24"})

    def test_rahu_ketu_opposition(self):
        positions = {p["code"]: p for p in self.result["charts"]["D1"]["positions"]}
        separation = (positions["Ketu"]["longitude"] - positions["Rahu"]["longitude"]) % 360.0
        self.assertAlmostEqual(separation, 180.0, places=8)

    def test_moon_is_first_house_in_moon_chart(self):
        moon = next(p for p in self.result["charts"]["Moon"]["positions"] if p["code"] == "Moon")
        self.assertEqual(moon["house"], 1)

    def test_dasha_periods_are_contiguous(self):
        periods = self.result["dasha"]["mahadashas"]
        for left, right in zip(periods, periods[1:]):
            self.assertEqual(left["end_utc"], right["start_utc"])

class TimezoneTests(unittest.TestCase):
    def test_nonexistent_new_york_time(self):
        result = resolve_local_time(datetime(2024, 3, 10, 2, 30), "America/New_York")
        self.assertEqual(result.status, "nonexistent")

    def test_ambiguous_new_york_time(self):
        result = resolve_local_time(datetime(2024, 11, 3, 1, 30), "America/New_York")
        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(len(result.choices_utc), 2)

if __name__ == "__main__":
    unittest.main()
