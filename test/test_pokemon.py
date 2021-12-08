import unittest

from pokemon import *
import data

class TestPokemon(unittest.TestCase):
    maxDiff = None
    def test_exp_given(self):
        spec = data.get_species('starmie')
        self.assertEqual(spec.name, 'Starmie')
        starmie = Pokemon('starmie', 21)
        self.assertEqual(starmie.exp_given(1), 931)

        spec = data.get_species('venusaur')
        venusaur = Pokemon('venusaur', 65)
        self.assertEqual(venusaur.exp_given(1), 2896)

    def test_print_possible_stats(self):
        nidoran = Pokemon('nidoranm', 4)
        exp_results = '''L4 NidoranM
Stat ranges WITHOUT badge boosts:
IV  |0   |1   |2   |3   |4   |5   |6   |7   |8   |9   |10  |11  |12  |13  |14  |15
------------------------------------------------------------------------------------
HP  |  17|  17|  17|  17|  18|  18|  18|  18|  18|  18|  18|  18|  18|  18|  18|  18
ATT |   9|   9|   9|   9|   9|   9|  10|  10|  10|  10|  10|  10|  10|  10|  10|  10
DEF |   8|   8|   8|   8|   8|   8|   8|   8|   8|   8|   9|   9|   9|   9|   9|   9
SPD |   9|   9|   9|   9|   9|   9|   9|   9|   9|   9|   9|   9|   9|  10|  10|  10
SPC |   8|   8|   8|   8|   8|   8|   8|   8|   8|   8|   9|   9|   9|   9|   9|   9
'''
        self.assertEqual(nidoran.print_possible_stats(), exp_results)

    def test_battle(self):
        nidoran = Pokemon('nidoranm', 4, ivs_from_hex(0xffef))

        geodude = Pokemon('geodude', 12)

        self.assertEqual(geodude.exp_given(2), 109)

        onix = Pokemon('onix', 14)

        self.assertEqual(onix.exp_given(2), 162)
        geodude.battle(nidoran, 2)
        onix.battle(nidoran, 2)

        exp_results = '''L8 NidoranM
Stat ranges WITHOUT badge boosts:
IV  |0   |1   |2   |3   |4   |5   |6   |7   |8   |9   |10  |11  |12  |13  |14  |15
------------------------------------------------------------------------------------
HP  |  25|  25|  25|  25|  26|  26|  26|  26|  26|  26|  27|  27|  27|  27|  27|  27
ATT |  14|  14|  14|  14|  14|  15|  15|  15|  15|  15|  15|  16|  16|  16|  16|  16
DEF |  11|  11|  11|  12|  12|  12|  12|  12|  12|  13|  13|  13|  13|  13|  13|  14
SPD |  13|  13|  13|  13|  13|  13|  14|  14|  14|  14|  14|  14|  15|  15|  15|  15
SPC |  11|  11|  11|  11|  12|  12|  12|  12|  12|  12|  13|  13|  13|  13|  13|  13
'''

        self.assertEqual(nidoran.print_possible_stats(), exp_results)
        self.assertEqual(nidoran.ev_hp, 37)
        self.assertEqual(nidoran.ev_att, 62)
        self.assertEqual(nidoran.ev_def, 130)
        self.assertEqual(nidoran.ev_spd, 45)
        self.assertEqual(nidoran.ev_spc, 30)
        self.assertEqual(nidoran._hp, 27)
        self.assertEqual(nidoran._att, 16)
        self.assertEqual(nidoran._def, 14)
        self.assertEqual(nidoran._spd, 15)
        self.assertEqual(nidoran._spc, 13)

        nidoran.ivs = ivs_from_hex(0x0000)
        nidoran.calculate_stats()
        self.assertEqual(nidoran._hp, 25)
        self.assertEqual(nidoran._att, 14)
        self.assertEqual(nidoran._def, 11)
        self.assertEqual(nidoran._spd, 13)
        self.assertEqual(nidoran._spc, 11)

        nidoran.ivs = ivs_from_hex(0xffef)
        nidoran.calculate_stats()
        self.assertEqual(nidoran._att, 16)

if __name__ == '__main__':
    unittest.main()

