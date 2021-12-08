import unittest

import route_parser
from ivs import ivs_from_hex

class TestRouteParser(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.squirtle_route = route_parser.RouteFile('example_routes/squirtle.yaml')
        self.nido_route = route_parser.RouteFile('example_routes/red.yaml')

    def test_parse_variation(self):
        variations = self.squirtle_route.actions[0]['fight']['variations']
        self.assertEqual(len(variations['all']), 4)
        vars = route_parser.parse_variations(variations, self.squirtle_route.pokemon.ivs)

        f1 = vars['all']['good_att']
        self.assertEqual(f1.name, 'good_att')
        self.assertEqual(f1.def_mod.defense, -1)
        self.assertEqual(f1.att_mod.attack, 0)
        self.assertEqual(f1.ivs, ivs_from_hex(0xffff))

        brock = self.squirtle_route.actions[5]['fight']['variations']
        brock_all = brock['all']
        brock_2 = brock[2]
        self.assertEqual(len(brock), 2)
        self.assertEqual(len(brock_all), 2)
        self.assertEqual(len(brock_2), 6)

    def test_parse_range_checks(self):
        range_checks = self.nido_route.actions[2]['fight']['range_check']
        self.assertIsNotNone(range_checks)
        ranges = self.nido_route.parse_range_checks(range_checks)
        self.assertEqual(len(ranges), 3)
        self.assertEqual(len(ranges[1]), 2)
        self.assertEqual(len(ranges[2]), 3)
        self.assertEqual(len(ranges[3]), 3)

        range1 = ranges[1]['2_bbs']
        self.assertEqual(range1['turns'], 2)
        self.assertEqual(len(range1['att_mods']), 2)
        self.assertEqual(len(range1['def_mods']), 2)

        range2 = ranges[1]['1_bb']
        self.assertEqual(range2['turns'], 2)
        self.assertEqual(len(range2['att_mods']), 2)
        self.assertEqual(len(range2['def_mods']), 2)

    def test_parse_wild_fight(self):
        ...

    def test_parse_trainer_fight(self):
        ...



if __name__ == '__main__':
    unittest.main()