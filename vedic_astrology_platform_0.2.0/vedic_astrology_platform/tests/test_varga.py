import unittest
from core.varga import varga_longitude

class VargaBoundaryTests(unittest.TestCase):
    def test_d2_odd_sign_halves(self):
        self.assertEqual(int(varga_longitude(0.0, 2) // 30), 4)
        self.assertEqual(int(varga_longitude(15.0, 2) // 30), 3)

    def test_d3_parts(self):
        self.assertEqual(int(varga_longitude(0.0, 3) // 30), 0)
        self.assertEqual(int(varga_longitude(10.0, 3) // 30), 4)
        self.assertEqual(int(varga_longitude(20.0, 3) // 30), 8)

    def test_d4_quarters(self):
        self.assertEqual([int(varga_longitude(x, 4) // 30) for x in (0.0, 7.5, 15.0, 22.5)], [0, 3, 6, 9])

    def test_d12_last_part(self):
        self.assertEqual(int(varga_longitude(29.999, 12) // 30), 11)

if __name__ == "__main__":
    unittest.main()
