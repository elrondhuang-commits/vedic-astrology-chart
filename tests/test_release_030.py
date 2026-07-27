import unittest
from datetime import datetime, timezone

from core.chart import calculate_chart
from core.constants import PROJECT_VERSION


class Release030Tests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(PROJECT_VERSION, "0.3.0")

    def test_full_chart_contains_new_vargas(self):
        result = calculate_chart(
            datetime(1990, 1, 1, 4, 0, tzinfo=timezone.utc),
            22.9999,
            120.2270,
            current_utc=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertEqual(result["schema_version"], "0.3.0")
        for code in ("D16", "D20", "D24"):
            with self.subTest(code=code):
                chart = result["charts"][code]
                self.assertEqual(chart["chart_code"], code)
                self.assertEqual(len(chart["positions"]), 10)
                self.assertEqual(
                    next(item for item in chart["positions"] if item["code"] == "Ascendant")["house"],
                    1,
                )


if __name__ == "__main__":
    unittest.main()
