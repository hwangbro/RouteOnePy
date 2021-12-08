import unittest

from stat_modifier import *
from pokemon import Pokemon

class TestStatModfier(unittest.TestCase):
    def test_has_mods(self):
        x = StatModifier()
        self.assertFalse(x.has_mods)
        x.attack = 1
        self.assertTrue(x.has_mods)
        x.attack = 0
        x.used_x_acc = True
        self.assertTrue(x.has_mods)

    def test_has_bbs(self):
        x = StatModifier()
        self.assertFalse(x.has_bbs)
        x.att_bb = 1
        self.assertTrue(x.has_bbs)

    def test_mods(self):
        nido = Pokemon('nidoranm', 6)
        x = StatModifier()
        self.assertEqual(x.mod_att(nido), 12)
        x.attack = 1
        self.assertEqual(x.mod_att(nido), 18)
        nido.att_badge = True
        self.assertEqual(x.mod_att(nido), 20)
        x.att_bb = 1
        self.assertEqual(x.mod_att(nido), 22)
        x.att_bb = 2
        self.assertEqual(x.mod_att(nido), 24)

        self.assertEqual(x.mod_def(nido), 10)
        x.defense = 1
        self.assertEqual(x.mod_def(nido), 15)
        nido.def_badge = True
        self.assertEqual(x.mod_def(nido), 16)
        x.def_bb = 1
        self.assertEqual(x.mod_def(nido), 18)
        x.def_bb = 2
        self.assertEqual(x.mod_def(nido), 20)

        self.assertEqual(x.mod_spd(nido), 11)
        x.speed = 1
        self.assertEqual(x.mod_spd(nido), 16)
        nido.spd_badge = True
        self.assertEqual(x.mod_spd(nido), 18)
        x.spd_bb = 1
        self.assertEqual(x.mod_spd(nido), 20)
        x.spd_bb = 2
        self.assertEqual(x.mod_spd(nido), 22)

        self.assertEqual(x.mod_spc(nido), 10)
        x.special = 1
        self.assertEqual(x.mod_spc(nido), 15)
        nido.spc_badge = True
        self.assertEqual(x.mod_spc(nido), 16)
        x.spc_bb = 1
        self.assertEqual(x.mod_spc(nido), 18)
        x.spc_bb = 2
        self.assertEqual(x.mod_spc(nido), 20)

    def test_repr(self):
        x = StatModifier()
        self.assertEqual(str(x), '<No Stat Modifications>')
        x.attack = 1
        x.special = -1
        self.assertEqual(str(x), '+[1/0/0/-1]')
        x.spd_bb = -1
        x.def_bb = 3
        self.assertEqual(str(x), '+[1/0/0/-1] +<0/3/-1/0>')
        x.used_x_acc = True
        self.assertEqual(str(x), '+[1/0/0/-1] +<0/3/-1/0> +X ACC')

    def test_parse_stat_mod(self):
        self.assertEqual(parse_stat_mod(None), StatModifier())
        mod_dict = {
            'bbs': '1/0/0/0'
        }
        self.assertEqual(parse_stat_mod(mod_dict), StatModifier(att_bb=1))
        mod_dict['stages'] = '6/0/0/0'
        self.assertEqual(parse_stat_mod(mod_dict), StatModifier(attack=6, att_bb=1))

        mod_dict = {
            1: {
                'stages': '0/0/0/0',
            },
            2: {
                'stages': '0/-1/0/0',
            }
        }
        x = parse_stat_mod(mod_dict)
        self.assertEqual(x[1], StatModifier())
        self.assertEqual(x[2], StatModifier(defense=-1))
        self.assertEqual(len(x), 2)

    def test_parse_stat_mod_range_checks(self):
        rc_dict = {
            'stages': '1/0/0/0',
            'turns': 1,
            'bbs': '2/0/0/0'
        }
        self.assertEqual(parse_stat_mod_range_checks(rc_dict, 2)[0], StatModifier(attack=1, att_bb=2))
        rc_dict = {
            'stages': '1/0/0/0, 2/0/0/0',
            'bbs': '2/0/0/0'
        }
        self.assertEqual(parse_stat_mod_range_checks(rc_dict, 2)[0], StatModifier(attack=1, att_bb=2))
        self.assertEqual(parse_stat_mod_range_checks(rc_dict, 2)[1], StatModifier(attack=2, att_bb=2))
        rc_dict = {
            'stages': '1/0/0/0, 2/0/0/0',
            'bbs': '2/0/0/0, -1/0/0/0'
        }
        self.assertEqual(parse_stat_mod_range_checks(rc_dict, 2)[0], StatModifier(attack=1, att_bb=2))
        self.assertEqual(parse_stat_mod_range_checks(rc_dict, 2)[1], StatModifier(attack=2, att_bb=-1))
        with self.assertRaises(IndexError):
            parse_stat_mod_range_checks(rc_dict, 3)

if __name__ == '__main__':
    unittest.main()
