import unittest

import data
# tests data integrity

class TestItems(unittest.TestCase):
    def test_basic(self):
        items = data.get_items()
        # raw items, doesn't count glitch items
        self.assertEqual(len(items), 144)
        self.assertEqual(items['IRON'].cost, 9800)

class TestLearnsets(unittest.TestCase):
    def test_basic(self):
        learnsets = data.get_learnsets()
        bulb_ls = learnsets['rb'][1]
        self.assertEqual(len(bulb_ls), 9)
        self.assertEqual(bulb_ls[0].move.name, 'Tackle')
        self.assertEqual(bulb_ls[0].level, 1)
        self.assertEqual(bulb_ls[1].move.name, 'Growl')
        self.assertEqual(bulb_ls[1].level, 1)
        self.assertEqual(bulb_ls[8].move.name, 'SolarBeam')
        self.assertEqual(bulb_ls[8].level, 48)

class TestSpecies(unittest.TestCase):
    def test_basic(self):
        species = data.get_all_species()
        self.assertEqual(len(species), 153)
        bulb = species['BULBASAUR']
        self.assertEqual(bulb.base_hp, 45)
        self.assertEqual(bulb.base_att, 49)
        self.assertEqual(bulb.base_def, 49)
        self.assertEqual(bulb.base_spd, 45)
        self.assertEqual(bulb.base_spc, 65)
        self.assertEqual(bulb.dex_num, 1)

class TestMoves(unittest.TestCase):
    def test_basic(self):
        moves = data.get_moves()
        self.assertEqual(len(moves), 166)
        headbutt = moves['HEADBUTT']
        self.assertEqual(headbutt.pp, 15)
        self.assertEqual(headbutt.power, 70)
        self.assertEqual(headbutt.accuracy, 100)

class TestTrainer(unittest.TestCase):
    trainers = data.get_trainers()

    def test_basic(self):
        self.assertEqual(len(TestTrainer.trainers['rb']), 392)
        self.assertEqual(len(TestTrainer.trainers['y']), 396)

    def test_special_trainers(self):
        y_lance = TestTrainer.trainers['y'][0x3A5A6]
        self.assertEqual(str(y_lance.pokes[0].moveset), 'Dragon Rage, Leer, Hydro Pump, Hyper Beam')
        self.assertEqual(str(y_lance.pokes[1].moveset), 'Thunder Wave, Slam, Thunderbolt, Hyper Beam')
        self.assertEqual(str(y_lance.pokes[2].moveset), 'BubbleBeam, Wrap, Ice Beam, Hyper Beam')
        self.assertEqual(str(y_lance.pokes[3].moveset), 'Wing Attack, Swift, Fly, Hyper Beam')
        self.assertEqual(str(y_lance.pokes[4].moveset), 'Blizzard, Fire Blast, Thunder, Hyper Beam')

        rb_rival = TestTrainer.trainers['rb'][0x3A491]
        self.assertEqual(str(rb_rival.pokes[0].moveset), 'Whirlwind, Wing Attack, Sky Attack, Mirror Move')

class TestTrainerClass(unittest.TestCase):
    def test_basic(self):
        trainer_classes = data.get_trainer_classes()
        self.assertEqual(len(trainer_classes), 48)
        self.assertEqual(trainer_classes['BRUNO'].base_money, 99)

class TestAliases(unittest.TestCase):
    def test_basic(self):
        aliases = data.get_trainer_aliases()
        self.assertEqual(len(aliases['rb']), 58)
        self.assertEqual(len(aliases['y']), 64)

        self.assertEqual(aliases['rb']['LORELEI'], 0x3a4bb)
        self.assertEqual(aliases['y']['LORELEI'], 0x3a53f)

if __name__ == '__main__':
    unittest.main()
