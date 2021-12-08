import unittest

from type import *

class TestType(unittest.TestCase):
    def test_effectiveness(self):
        fire_grass = TypeEffectiveness(Type.Fire, Type.Grass)
        self.assertEqual(fire_grass.effectiveness, Effectiveness.SuperEffective)
        self.assertEqual(effectiveness(Type.Fire, Type.Water, Type.Rock), Effectiveness.VeryWeak)
        self.assertEqual(effectiveness(Type.Dragon, Type.Dragon), Effectiveness.SuperEffective)

    def test_damage(self):
        self.assertEqual(apply_effectiveness(100, Type.Fire, Type.Grass), 200)
        self.assertEqual(apply_effectiveness(100, Type.Fire, Type.Water, Type.Rock), 25)
        self.assertEqual(apply_effectiveness(100, Type.Ground, Type.Grass), 50)
        self.assertEqual(apply_effectiveness(100, Type.Normal, Type.Normal), 100)
        self.assertEqual(apply_effectiveness(100, Type.Normal, Type.Ghost), 0)
        self.assertEqual(apply_effectiveness(100, Type.Ghost, Type.Normal), 0)

if __name__ == '__main__':
    unittest.main()