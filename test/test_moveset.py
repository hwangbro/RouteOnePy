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

if __name__ == '__main__':
    unittest.main()
