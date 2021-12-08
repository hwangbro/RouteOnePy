import unittest

from pokemon import Pokemon
from ivs import ivs_from_hex
from battle import *
from route_parser import RouteFile, parse_variations
from stat_modifier import parse_stat_mod
import data

class TestBattle(unittest.TestCase):
    trainers = data.get_trainers()['rb']
    aliases = data.get_trainer_aliases()['rb']
    moves = data.get_moves()

    def __init__(self, *args, **kwargs):
        self.maxDiff = None
        super().__init__(*args, **kwargs)

    def test_basic_battle(self):
        nidoran = Pokemon('nidoranm', 4, ivs_from_hex(0xffef))
        brock = self.trainers[self.aliases['BROCK']]
        self.assertEqual(brock.trainer_class.name, 'BROCK')
        battle = Battle(nidoran, brock, participants=2, verbosity=2, variations=dict())
        summary = battle.battle()
        # summary = brock.battle(nidoran, participants=2, verbose=2)
        exp = '\nBROCK (0x3a3b5: L12 Geodude, L14 Onix) Prize 1386\n'
        exp += 'LVL 4 EXP NEEDED: 39/39\n'
        exp += 'L4 NidoranM vs L12 Geodude          >>> EXP GIVEN: 220\n'
        exp += 'NidoranM (18/10/9/10/9)\n'
        exp += 'Leer\n'
        exp += 'Tackle 1-1\t(crit: 1-1)\n'
        exp += '\tNormal rolls: 1x39\n'
        exp += '\tCrit rolls: 1x39\n\n'
        exp += 'Geodude (33/26/30/11/14)\n'
        exp += 'Tackle 11-14\t(crit: 20-24)\n'
        exp += '\tNormal rolls: 11x2, 12x18, 13x18, 14x1\n'
        exp += '\tCrit rolls: 18x39\n'
        exp += '\t(Overall 1-hit Kill%: 3.9062%)\n'
        exp += 'Defense Curl\n\n'

        exp += 'LVL 6 EXP NEEDED: 31/57\n'
        exp += 'L6 NidoranM vs L14 Onix          >>> EXP GIVEN: 324\n'
        exp += 'NidoranM (23/13/11/12/11)\n'
        exp += 'Leer\n'
        exp += 'Tackle 1-1\t(crit: 1-1)\n'
        exp += '\tNormal rolls: 1x39\n'
        exp += '\tCrit rolls: 1x39\n\n'
        exp += 'Onix (36/20/52/26/15)\n'
        exp += 'Tackle 8-10\t(crit: 15-18)\n'
        exp += '\tNormal rolls: 8x13, 9x25, 10x1\n'
        exp += '\tCrit rolls: 15x10, 16x14, 17x14, 18x1\n'
        exp += '\t(Overall 2-hit Kill%: 25.4745%)\n'
        exp += 'Screech\nBide\n\n'

        self.assertEqual(summary, exp)

    def test_basic_battle_with_variations(self):
        squirtle_route = RouteFile('example_routes/squirtle.yaml')
        brock_variations = squirtle_route.actions[5]['fight']['variations']
        vars = parse_variations(brock_variations, squirtle_route.pokemon.ivs)
        nidoran = Pokemon('nidoranm', 4, ivs_from_hex(0xffef))
        brock = self.trainers[self.aliases['BROCK']]
        self.assertEqual(brock.trainer_class.name, 'BROCK')
        battle = Battle(nidoran, brock, participants=2, verbosity=2, variations=vars)
        with open('test/examples/brock_variations.txt') as f:
            exp_brock_vars = ''.join(f.readlines())
        self.assertEqual(exp_brock_vars, battle.battle())

    def test_basic_wild_battle_with_variations(self):
        squirtle_route = RouteFile('example_routes/squirtle.yaml')
        pidgey_variations = squirtle_route.actions[2]['wild']['variations']
        vars = parse_variations(pidgey_variations, squirtle_route.pokemon.ivs)
        squirtle = Pokemon('squirtle', 5, ivs_from_hex(0xffff))
        rat = Pokemon('rattata', 3, ivs_from_hex(0x0000), True)
        battle = Battle(squirtle, rat, verbosity=2, variations=vars, wild=True)
        with open('test/examples/rat_variations.txt') as f:
            exp_rat_vars = ''.join(f.readlines())
        self.assertEqual(exp_rat_vars, battle.battle())

    def test_basic_battle_with_specific_mods(self):
        nido_route = RouteFile('example_routes/red.yaml')
        nidoran = nido_route.pokemon
        battle = Battle(nidoran, self.trainers[self.aliases['BROCK']], participants=2, verbosity=0)
        battle.battle()
        nidoran.att_badge = True
        nidoran.moveset.add_move(self.moves['HORN ATTACK'])
        self.assertTrue(nidoran.att_badge)
        battle = Battle(nidoran, self.trainers[self.aliases['BC1']], verbosity=0)
        battle.battle()

        att_mods = nido_route.actions[3]['fight']['att_mod']
        att_mods = parse_stat_mod(att_mods)
        def_mods = nido_route.actions[3]['fight']['def_mod']
        def_mods = parse_stat_mod(def_mods)
        battle = Battle(nidoran, self.trainers[self.aliases['SHORTS GUY']], verbosity=2, att_mod=att_mods, def_mod=def_mods)
        with open('test/examples/shorts_guy.txt') as f:
            exp_shorts = ''.join(f.readlines())
        self.assertEqual(exp_shorts, battle.battle())
        battle = Battle(nidoran, self.trainers[self.aliases['BC2']], verbosity=0)
        battle.battle()
        battle = Battle(nidoran, self.trainers[self.aliases['BC3']], verbosity=0)
        battle.battle()
        nidoran.moveset.add_move(self.moves['POISON STING'])
        def_mods = parse_stat_mod(nido_route.actions[6]['fight']['def_mod'])
        battle = Battle(nidoran, self.trainers[self.aliases['MOON ROCKET']], verbosity=2, def_mod=def_mods)
        with open('test/examples/moon_rocket.txt') as f:
            exp_moon_rocket = ''.join(f.readlines())

        self.assertEqual(exp_moon_rocket, battle.battle())


    def test_basic_range_check(self):
        nido_route = RouteFile('example_routes/red.yaml')
        nidoran = Pokemon('nidoranm', 4, ivs_from_hex(0xffef))
        brock = self.trainers[self.aliases['BROCK']]
        battle = Battle(nidoran, brock, participants=2, verbosity=0)
        battle.battle()
        nidoran.att_badge = True
        nidoran.moveset.add_move(self.moves['HORN ATTACK'])
        bc1 = self.trainers[self.aliases['BC1']]
        range_checks = nido_route.actions[2]['fight']['range_check']
        range_checks = nido_route.parse_range_checks(range_checks)
        battle = Battle(nidoran, bc1, range_checks=range_checks, verbosity=2)
        with open('test/examples/bc1_ranges.txt') as f:
            exp_bc1_ranges = ''.join(f.readlines())
        self.assertEqual(exp_bc1_ranges, battle.battle())
