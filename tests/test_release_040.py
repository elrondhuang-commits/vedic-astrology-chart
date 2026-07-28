import unittest
from datetime import datetime, timezone

from core.chart import calculate_chart
from core.constants import PROJECT_VERSION


class Release040Tests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(PROJECT_VERSION, "0.4.0")

    def test_full_chart_contains_complete_shodashavarga(self):
        result = calculate_chart(
            datetime(1990, 1, 1, 4, 0, tzinfo=timezone.utc),
            22.9999,
            120.2270,
            current_utc=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        expected = (
            "D1", "Moon", "D2", "D3", "D4", "D7", "D9", "D10",
            "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
        )
        self.assertEqual(result["schema_version"], "0.4.0")
        self.assertEqual(tuple(result["charts"]), expected)
        for code in expected[2:]:
            with self.subTest(code=code):
                chart = result["charts"][code]
                self.assertEqual(chart["chart_code"], code)
                self.assertEqual(len(chart["positions"]), 10)
                asc = next(item for item in chart["positions"] if item["code"] == "Ascendant")
                self.assertEqual(asc["house"], 1)


if __name__ == "__main__":
    unittest.main()
