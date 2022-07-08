import unittest
from moveset import *
from data import *

class TestMoveset(unittest.TestCase):
    def setUp(self) -> None:
        self.moves = get_moves()
    def test_add_move(self):
        x = Moveset()
        x.add_move(self.moves['TACKLE'])
        self.assertEqual(len(x), 1)
        self.assertEqual(x[0].name, 'Tackle')
        x.add_move(self.moves['TACKLE'])
        self.assertEqual(len(x), 1)
        x.add_move(self.moves['HORN ATTACK'])
        self.assertEqual(len(x), 2)

    def test_delete_move(self):
        x = Moveset()
        x.add_move(self.moves['TACKLE'])
        x.add_move(self.moves['HORN ATTACK'])
        self.assertEqual(len(x), 2)
        x.delete_move(self.moves['POISON STING'])
        self.assertEqual(len(x), 2)
        x.delete_move(self.moves['HORN ATTACK'])
        self.assertEqual(len(x), 1)

    def test_set_move(self):
        x = Moveset()
        x.add_move(self.moves['TACKLE'])
        x.add_move(self.moves['HORN ATTACK'])
        x.set_move(0, self.moves['POISON STING'])
        self.assertEqual(len(x), 2)
        self.assertEqual(x[0].name, 'Poison Sting')

        x.add_move(self.moves['HORN ATTACK'])
        x.add_move(self.moves['DOUBLE KICK'])
        x.set_move(3, self.moves['THRASH'])
        self.assertEqual(len(x), 4)
        self.assertEqual(x[3].name, 'Thrash')

class TestDefaultMoveset(unittest.TestCase):
    def test_basic_case(self):
        bulba = get_learnset(1)
        default_moveset = get_default_moveset(bulba, 1)
        self.assertEqual(len(default_moveset), 2)
        self.assertEqual(default_moveset[0].name, 'Tackle')
        self.assertEqual(default_moveset[1].name, 'Growl')

        default_moveset = get_default_moveset(bulba, 100)
        self.assertEqual(len(default_moveset), 4)
        self.assertEqual(default_moveset[0].name, 'Razor Leaf')
        self.assertEqual(default_moveset[1].name, 'Growth')
        self.assertEqual(default_moveset[2].name, 'Sleep Powder')
        self.assertEqual(default_moveset[3].name, 'SolarBeam')

    def test_moveset_duplicates(self):
        pidgeotto = get_learnset(17)
        default_moveset_l1 = get_default_moveset(pidgeotto, 1)
        self.assertEqual(len(default_moveset_l1), 2)
        self.assertEqual(default_moveset_l1[0].name, 'Gust')
        self.assertEqual(default_moveset_l1[1].name, 'Sand-Attack')
        default_moveset_l5 = get_default_moveset(pidgeotto, 5)
        self.assertEqual(len(default_moveset_l5), 2)
        self.assertEqual(default_moveset_l5[0].name, 'Gust')
        self.assertEqual(default_moveset_l5[1].name, 'Sand-Attack')

        victreebel = get_learnset(71)
        default_moveset_l1 = get_default_moveset(victreebel, 1)
        self.assertEqual(len(default_moveset_l1), 4)
        self.assertEqual(default_moveset_l1[0].name, 'Sleep Powder')
        self.assertEqual(default_moveset_l1[1].name, 'Stun Spore')
        self.assertEqual(default_moveset_l1[2].name, 'Acid')
        self.assertEqual(default_moveset_l1[3].name, 'Razor Leaf')
        default_moveset_l18 = get_default_moveset(victreebel, 18)
        self.assertEqual(len(default_moveset_l18), 4)
        self.assertEqual(default_moveset_l18[0].name, 'Razor Leaf')
        self.assertEqual(default_moveset_l18[1].name, 'Wrap')
        self.assertEqual(default_moveset_l18[2].name, 'PoisonPowder')
        self.assertEqual(default_moveset_l18[3].name, 'Sleep Powder')


if __name__ == '__main__':
    unittest.main()
