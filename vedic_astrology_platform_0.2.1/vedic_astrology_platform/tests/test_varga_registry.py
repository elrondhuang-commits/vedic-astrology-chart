import unittest

from core.varga_registry import SUPPORTED_VARGA_CODES, VARGA_REGISTRY, get_varga_info


class VargaRegistryTests(unittest.TestCase):
    def test_expected_codes_are_registered(self):
        self.assertEqual(
            SUPPORTED_VARGA_CODES,
            ("D2", "D3", "D4", "D7", "D9", "D10", "D12"),
        )

    def test_every_entry_has_bilingual_ui_text(self):
        for code, info in VARGA_REGISTRY.items():
            with self.subTest(code=code):
                self.assertTrue(info.labels["zh-TW"])
                self.assertTrue(info.labels["en"])
                self.assertTrue(info.descriptions["zh-TW"])
                self.assertTrue(info.descriptions["en"])
                self.assertTrue(info.reference)

    def test_unknown_code_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Unsupported varga code"):
            get_varga_info("D99")


if __name__ == "__main__":
    unittest.main()
