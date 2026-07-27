import unittest

from core.varga import varga_longitude


def sign_of(longitude: float, division: int) -> int:
    return int(varga_longitude(longitude, division) // 30)


class VargaBoundaryTests(unittest.TestCase):
    def test_d2_odd_sign_halves(self):
        self.assertEqual(sign_of(0.0, 2), 4)
        self.assertEqual(sign_of(15.0, 2), 3)

    def test_d3_parts(self):
        self.assertEqual(sign_of(0.0, 3), 0)
        self.assertEqual(sign_of(10.0, 3), 4)
        self.assertEqual(sign_of(20.0, 3), 8)

    def test_d4_quarters(self):
        self.assertEqual(
            [sign_of(value, 4) for value in (0.0, 7.5, 15.0, 22.5)],
            [0, 3, 6, 9],
        )

    def test_d12_last_part(self):
        self.assertEqual(sign_of(29.999, 12), 11)

    def test_d16_modality_start_signs(self):
        # Aries is movable, Taurus fixed, Gemini dual.
        self.assertEqual(sign_of(0.0, 16), 0)
        self.assertEqual(sign_of(30.0, 16), 4)
        self.assertEqual(sign_of(60.0, 16), 8)

    def test_d16_segment_boundary(self):
        segment = 30.0 / 16.0
        self.assertEqual(sign_of(0.0, 16), 0)
        self.assertEqual(sign_of(segment, 16), 1)
        self.assertEqual(sign_of(segment - 1e-9, 16), 0)

    def test_d20_modality_start_signs(self):
        # Aries is movable, Taurus fixed, Gemini dual.
        self.assertEqual(sign_of(0.0, 20), 0)
        self.assertEqual(sign_of(30.0, 20), 8)
        self.assertEqual(sign_of(60.0, 20), 4)

    def test_d20_segment_boundary(self):
        self.assertEqual(sign_of(1.5 - 1e-9, 20), 0)
        self.assertEqual(sign_of(1.5, 20), 1)

    def test_d24_odd_even_start_signs(self):
        self.assertEqual(sign_of(0.0, 24), 4)   # Aries -> Leo
        self.assertEqual(sign_of(30.0, 24), 3)  # Taurus -> Cancer

    def test_d24_segment_boundary(self):
        self.assertEqual(sign_of(1.25 - 1e-9, 24), 4)
        self.assertEqual(sign_of(1.25, 24), 5)

    def test_varga_degree_is_scaled_within_segment(self):
        # Halfway through the first D20 segment becomes 15 degrees in its
        # mapped sign.
        result = varga_longitude(0.75, 20)
        self.assertAlmostEqual(result % 30.0, 15.0, places=9)


if __name__ == "__main__":
    unittest.main()
