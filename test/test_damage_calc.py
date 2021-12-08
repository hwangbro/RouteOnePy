import unittest

from damage_calc import *
from pokemon import *
from data import get_move
from stat_modifier import StatModifier
from ivs import IVs, ivs_from_hex

class TestDamageCalc(unittest.TestCase):
    def test_basic_damage(self):
        squirtle = Pokemon('squirtle', 5, ivs = ivs_from_hex(0xffef))
        bulbasaur = Pokemon('bulbasaur', 5)
        tackle = get_move('tackle')
        dmg_calc = DamageCalc(tackle, squirtle, bulbasaur, StatModifier(), StatModifier(defense=-1))
        self.assertEqual(dmg_calc.damage(217), 5)
        self.assertEqual(dmg_calc.damage(255), 7)
        self.assertEqual(dmg_calc.damage(217, True), 5)
        self.assertEqual(dmg_calc.damage(255, True), 6)

        self.assertEqual(dmg_calc.min_damage(), 5)
        self.assertEqual(dmg_calc.min_damage(True), 5)
        self.assertEqual(dmg_calc.max_damage(), 7)
        self.assertEqual(dmg_calc.max_damage(True), 6)

    def test_range_rolls(self):
        ...

    def test_range_prob_rolls(self):
        ...

    def test_simple_summary(self):
        nidoran = Pokemon('nidoranm', 4, ivs = IVs(15, 15, 14, 15))
        geodude = Pokemon('geodude', 12)
        onix = Pokemon('onix', 14)

        geodude.battle(nidoran, 2)
        onix.battle(nidoran, 2)
        nidoran.att_badge = True

        caterpie = Pokemon('caterpie', 10)
        horn_attack = get_move('horn attack')
        self.assertEqual(horn_attack.power, 65)
        stat_mod = StatModifier()
        dmg_calc = DamageCalc(horn_attack, nidoran, caterpie, stat_mod, stat_mod)
        self.assertEqual(nidoran.level, 8)
        self.assertEqual(nidoran.attack, 18)
        self.assertEqual(caterpie.defense, 13)
        exp_summary = 'Horn Attack 9-11\t(crit: 11-14)\n'
        exp_summary += '\tNormal rolls: 9x15, 10x23, 11x1\n'
        exp_summary += '\tCrit rolls: 11x2, 12x18, 13x18, 14x1\n'
        exp_summary += '\t(Overall 3-hit Kill%: 46.0897%)'
        self.assertEqual('\n'.join(dmg_calc.summary), exp_summary)

        tackle = get_move('tackle')
        dmg_calc.move = tackle
        exp_summary = 'Tackle 5-6\t(crit: 6-8)\n'
        exp_summary += '\tNormal rolls: 5x38, 6x1\n'
        exp_summary += '\tCrit rolls: 6x7, 7x31, 8x1\n'
        exp_summary += '\t(Overall 5-hit Kill%: 1.3762%)'
        self.assertEqual('\n'.join(dmg_calc.summary), exp_summary)

        caterpie.battle(nidoran)
        weedle = Pokemon('weedle', 10)
        weedle.battle(nidoran)
        caterpie.battle(nidoran)

        rat = Pokemon('rattata', 11)
        def_down = StatModifier(defense=-1)
        dmg_calc = DamageCalc(horn_attack, nidoran, rat, stat_mod, def_down)
        self.assertEqual(nidoran.level, 10)
        self.assertEqual(nidoran.attack, 21)
        self.assertEqual(rat.defense, 14)
        self.assertEqual(def_down.mod_def(rat), 9)

        exp_summary = 'Horn Attack 17-20\t(crit: 16-19)\n'
        exp_summary += '\tNormal rolls: 17x13, 18x13, 19x12, 20x1\n'
        exp_summary += '\tCrit rolls: 16x12, 17x13, 18x13, 19x1'
        self.assertEqual('\n'.join(dmg_calc.summary), exp_summary)

        dmg_calc = DamageCalc(tackle, nidoran, rat, stat_mod, def_down)
        exp_summary = 'Tackle 9-11\t(crit: 9-11)\n'
        exp_summary += '\tNormal rolls: 9x15, 10x23, 11x1\n'
        exp_summary += '\tCrit rolls: 9x15, 10x23, 11x1\n'
        exp_summary += '\t(Overall 3-hit Kill%: 68.1384%)'
        self.assertEqual('\n'.join(dmg_calc.summary), exp_summary)

    def test_n_shot_percent(self):
        nidoran = Pokemon('nidoranm', 4, ivs = IVs(15, 15, 14, 15))
        geodude = Pokemon('geodude', 12)
        onix = Pokemon('onix', 14)

        tackle = get_move('tackle')

        chance = n_shot_with_mods(geodude, nidoran, 1, [tackle], [StatModifier()], [StatModifier()], True)
        self.assertEqual(round(chance, 4), 3.9062)

        geodude.battle(nidoran, 2)
        onix.battle(nidoran, 2)
        nidoran.att_badge = True

        caterpie = Pokemon('caterpie', 10)
        horn_attack = get_move('horn attack')
        tackle = get_move('tackle')
        self.assertEqual(horn_attack.power, 65)
        stat_mod = StatModifier()
        stat_mod_1 = StatModifier(defense=-1)
        stat_mod_2 = StatModifier(att_bb = 1)
        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, horn_attack], [stat_mod, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 65.70621)
        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, horn_attack], [stat_mod, stat_mod], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 4), 15.4289)
        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, horn_attack], [stat_mod_2, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 85.09552)

        caterpie.battle(nidoran)
        weedle = Pokemon('weedle', 10)
        chance = n_shot_with_mods(nidoran, weedle, 2, [horn_attack, tackle], [stat_mod_2, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 93.16013)
        chance = n_shot_with_mods(nidoran, weedle, 2, [horn_attack, tackle], [stat_mod, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 74.93208)
        chance = n_shot_with_mods(nidoran, weedle, 2, [horn_attack, tackle], [stat_mod, stat_mod], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 47.09813)
        weedle.battle(nidoran)

        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, tackle], [stat_mod, stat_mod], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 91.74359)
        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, tackle], [stat_mod, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 96.77422)
        chance = n_shot_with_mods(nidoran, caterpie, 2, [horn_attack, tackle], [stat_mod_2, stat_mod_2], [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 5), 99.16648)
        caterpie.battle(nidoran)
        rat = Pokemon('rattata', 11)
        chance = n_shot_with_mods(nidoran, rat, 3,
                    [tackle, tackle, tackle],
                    [stat_mod, stat_mod, stat_mod],
                    [stat_mod_1, stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 4), 68.1384)
        chance = n_shot_with_mods(nidoran, rat, 2,
                    [horn_attack, tackle],
                    [stat_mod, stat_mod],
                    [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 4), 20.4083)

        chance = n_shot_with_mods(nidoran, rat, 2,
                    [horn_attack, tackle],
                    [stat_mod, stat_mod_2],
                    [stat_mod_1, stat_mod_1])
        self.assertEqual(round(chance, 4), 47.0981)

if __name__ == '__main__':
    unittest.main()
