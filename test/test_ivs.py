import unittest
from ivs import *

class TestIVs(unittest.TestCase):
    def test_calculate_hp(self):
        x = IVs()
        self.assertEqual(x.hp, 8)
        self.assertEqual(x.hex, 0x9888)
        x = IVs(0, 0, 0, 0)
        self.assertEqual(x.hp, 0)
        self.assertEqual(x.hex, 0x0000)
        x = IVs(1, 1, 1, 1)
        self.assertEqual(x.hp, 15)
        self.assertEqual(x.hex, 0x1111)

    def test_from_hex(self):
        x = ivs_from_hex(0xffef)
        self.assertEqual(x.hp, 13)
        self.assertEqual(x.attack, 15)
        self.assertEqual(x.defense, 15)
        self.assertEqual(x.speed, 14)
        self.assertEqual(x.special, 15)


if __name__ == '__main__':
    unittest.main()
