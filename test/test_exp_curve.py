import unittest
from exp_curve import *

class TestExpCurve(unittest.TestCase):
    def setUp(self) -> None:
        self.slow = ExpCurve.Slow
        self.medium = ExpCurve.Medium
        self.medium_slow = ExpCurve.Medium_Slow
        self.fast = ExpCurve.Fast

    def test_exp_for_level(self):
        self.assertEqual(self.slow.exp_for_level(6), 158)
        self.assertEqual(self.slow.exp_for_level(100), 37876)
        self.assertEqual(self.medium_slow.exp_for_level(6), 57)
        self.assertEqual(self.medium_slow.exp_for_level(100), 33446)
        self.assertEqual(self.medium.exp_for_level(6), 127)
        self.assertEqual(self.medium.exp_for_level(100), 30301)
        self.assertEqual(self.fast.exp_for_level(6), 102)
        self.assertEqual(self.fast.exp_for_level(100), 24240)

    def test_exp_to_next_level(self):
        self.assertEqual(self.slow.exp_to_next_lvl(5, 100), 170)
        self.assertEqual(self.slow.exp_to_next_lvl(99, 0), 1250000)
        self.assertEqual(self.medium_slow.exp_to_next_lvl(5, 100), 79)
        self.assertEqual(self.medium_slow.exp_to_next_lvl(99, 0), 1059860)
        self.assertEqual(self.medium.exp_to_next_lvl(5, 100), 116)
        self.assertEqual(self.medium.exp_to_next_lvl(99, 0), 1000000)
        self.assertEqual(self.fast.exp_to_next_lvl(5, 100), 72)
        self.assertEqual(self.fast.exp_to_next_lvl(99, 0), 800000)

if __name__ == '__main__':
    unittest.main()
