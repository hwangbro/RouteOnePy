import unittest

import item

class TestItem(unittest.TestCase):
    def test_basic_price(self):
        x = item.Item('Potion', 0, 200)
        self.assertEqual(x.sell_price, 100)
        x.cost = 75
        self.assertEqual(x.sell_price, 37)
