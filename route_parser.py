import yaml
import re
from collections import defaultdict
from pathlib import Path

from pokemon import Pokemon
from ivs import ivs_from_hex
import stat_modifier
from battle import Battle
from fight_variation import FightVariation
import data

class RouteFile:
    def __init__(self, route_file: str):
        with open(route_file) as f:
            self.route = yaml.safe_load(f)

        base_name = Path(route_file).stem
        self.actions = self.route['route']
        self.config = self.route['config']
        self.game = self.config['game']
        self.output = self.config.get('output', f'{base_name}_output.txt')
        self.ivs = ivs_from_hex(self.config['ivs'])
        self.pokemon = Pokemon(self.config['species'], self.config['level'], self.ivs)
        self.verbosity = self.config.get('default_verbosity', 0)
        self.money = self.config.get('starting_money', 0)

        self.wild_regex = r'(?i)^(lvl|lv|l)(\d+) (.+)$'

        self.aliases = data.get_trainer_aliases()[self.game]
        self.trainers = data.get_game_trainers(self.game)
        self.species = data.get_all_species()
        self.moves = data.get_moves()

    def parse(self):
        self.log = ''
        for action in self.actions:
            if details := action.get('fight'):
                self.parse_fight(details)
            if details := action.get('wild'):
                self.parse_fight(details, True)
            elif move_name := action.get('learn move'):
                self.parse_learn_move(move_name, self.pokemon.moveset.add_move)
            elif move_name := action.get('unlearn move'):
                self.parse_learn_move(move_name, self.pokemon.moveset.delete_move)
            elif item_name := action.get('use item'):
                self.parse_item(item_name)
            elif details := action.get('print stats'):
                self.log += f'\n{self.pokemon.print_possible_stats()}\n'
            elif badge_name := action.get('get badge'):
                self.add_badge(badge_name)
            elif species := action.get('evolve'):
                self.pokemon.evolve(species)
            elif action := action.get('print money'):
                self.log += f'\nCurrent money: {self.money}\n'

    def add_badge(self, badge):
        badge = badge.lower()
        if badge in {'boulderbadge', 'boulder', 'attack', 'atk', 'att'}:
            self.pokemon.att_badge = True
        elif badge in {'souldbadge', 'soul', 'defense', 'def'}:
            self.pokemon.def_badge = True
        elif badge in {'thunderbadge', 'thunder', 'speed', 'spd'}:
            self.pokemon.spd_badge = True
        elif badge in {'volcanobadge', 'volcano', 'special', 'spc', 'spec'}:
            self.pokemon.spc_badge = True
        else:
            raise BadItemIdentifierException(f'Could not parse badge name ({badge})')

    def parse_fight(self, details, wild=False):
        participants = details.get('split', 1)
        verbosity = details.get('verbose', self.verbosity)

        att_mod = details.get('att_mod', None)
        def_mod = details.get('def_mod', None)

        att_mod = stat_modifier.parse_stat_mod(att_mod)
        def_mod = stat_modifier.parse_stat_mod(def_mod)

        if not wild:
            self.parse_trainer(details, participants, att_mod, def_mod, verbosity)
        else:
            self.parse_wild_fight(details, participants, att_mod, def_mod, verbosity)

    def parse_trainer(self, fight_details, participants, att_mod, def_mod, verbosity):
        trainers = []
        if t := fight_details.get('id', ''):
            if not isinstance(t, list):
                t = [t]
            for identifier in t:
                # offset
                if isinstance(identifier, int):
                    if trainer := self.trainers.get(identifier):
                        trainers.append(trainer)
                    else:
                        raise BadTrainerIdentifierException(f'Bad offset: {identifier}')
                elif isinstance(identifier, str):
                    if offset := self.aliases.get(identifier):
                        trainers.append(self.trainers[offset])
                    else:
                        raise BadTrainerIdentifierException(f'Bad alias: {identifier}')

        variations = fight_details.get('variations', dict())
        if variations and len(trainers) > 1:
            raise ValueError('Cannot specify both variations and multiple trainers')
        variations = parse_variations(variations, self.pokemon.ivs)

        range_checks = fight_details.get('range_check', dict())
        if range_checks and len(trainers) > 1:
            raise ValueError('Cannot specity both range checks and multiple trainers')
        range_checks = self.parse_range_checks(range_checks)

        for trainer in trainers:
            trainer_name = trainer.trainer_class.name
            print(trainer_name)
            battle = Battle(self.pokemon, trainer, variations, range_checks, att_mod, def_mod, participants, verbosity)
            self.log += battle.battle()
            self.money += trainer.prize_money

            if trainer_name == 'BROCK':
                self.pokemon.att_badge = True
            elif trainer_name == 'LTSURGE':
                self.pokemon.def_badge = True
            elif trainer_name == 'KOGA':
                self.pokemon.spd_badge = True
            elif trainer_name == 'BLAINE':
                self.pokemon.spc_badge = True

    def parse_wild_fight(self, fight_details, participants, att_mod, def_mod, verbosity):
        ivs = fight_details.get('ivs', 0x9888)
        pokes = []
        if t := fight_details.get('id', ''):
            if not isinstance(t, list):
                t = [t]
            for name in t:
                if match := re.match(self.wild_regex, name):
                    level = int(match.group(2))
                    species = match.group(3)
                    if spec := self.species.get(species.upper()):
                        pokes.append(Pokemon(spec, level, ivs_from_hex(ivs), True, self.game))
                    else:
                        raise BadWildIdentifierException(f'Could not identify wild species: {spec}')
                else:
                    raise BadWildIdentifierException(f'Could not identify wild fight {name}')

        variations = fight_details.get('variations', dict())
        if variations and len(pokes) > 1:
            raise ValueError('Cannot specify both variations and multiple wild pokemon')
        variations = parse_variations(variations, self.pokemon.ivs)

        range_checks = fight_details.get('range_check', dict())
        if range_checks and len(pokes) > 1:
            raise ValueError('Cannot specity both range checks and multiple wild pokemon')
        range_checks = self.parse_range_checks(range_checks)

        for wild in pokes:
            battle = Battle(self.pokemon, wild, variations, range_checks, att_mod, def_mod, participants, verbosity, True)
            self.log += battle.battle()

    def parse_range_checks(self, details: dict) -> dict:
        # keys = pokemon party index, value = range check
        ranges = {}

        # store turns, moves, att_mods, def_mods, lists or singles
        for idx, pokemon in details.items():
            if idx not in ranges:
                ranges[idx] = defaultdict(dict)
            for name, range_details in pokemon.items():
                if not (turns := range_details.get('turns')):
                    raise TypeError(f'Must specify number of turns.')
                if not (moves := range_details.get('moves')):
                    raise TypeError(f'Must specify at least one move.')

                ranges[idx][name]['turns'] = turns
                move_names = moves.split(',')
                if len(move_names) > 1:
                    ranges[idx][name]['moves'] = [self.moves[move.strip().upper()] for move in move_names]
                else:
                    ranges[idx][name]['moves'] = self.moves[moves.strip().upper()]
                att_mods = range_details.get('att_mod', dict())
                ranges[idx][name]['att_mods'] = stat_modifier.parse_stat_mod_range_checks(att_mods, turns)
                def_mods = range_details.get('def_mod', dict())
                ranges[idx][name]['def_mods'] = stat_modifier.parse_stat_mod_range_checks(def_mods, turns)

        return ranges

    def parse_item(self, item_name):
        if not isinstance(item_name, list):
            item_name = [item_name]

        for item in item_name:
            if item == 'RARE CANDY':
                self.pokemon.use_candy()
            elif item in {'PROTEIN', 'IRON', 'CARBOS', 'CALCIUM', 'HP UP'}:
                self.pokemon.use_vitamin(item)
            else:
                raise BadItemIdentifierException(f'Could not identify item {item}')

    def parse_learn_move(self, move_name, func):
        if not isinstance(move_name, list):
            move_name = [move_name]
        for move in move_name:
            m = self.moves[move.upper()]
            func(m)

    def write_file(self):
        with open(self.output, 'w') as f:
            f.write(self.log)

def parse_variations(details, poke_ivs):
    variations = {}

    for k,v in details.items():
        if k not in variations:
            variations[k] = {}
        for name, variation in v.items():
            ivs = ivs_from_hex(variation.get('ivs', poke_ivs.hex))
            wild_ivs = ivs_from_hex(variation.get('wild_ivs', 0x9888))
            att_mod = stat_modifier.parse_stat_mod(variation.get('att_mod'))
            def_mod = stat_modifier.parse_stat_mod(variation.get('def_mod'))
            variations[k][name] = FightVariation(name, att_mod, def_mod, ivs, wild_ivs)

    return variations

class RouteException(Exception):
    pass

class BadTrainerIdentifierException(RouteException):
    pass

class BadItemIdentifierException(RouteException):
    pass

class BadWildIdentifierException(RouteException):
    pass

if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        try:
            route = RouteFile(f)
            route.parse()
            route.write_file()
        except RouteException as e:
            print(f'Raised error: {e}')
    input('Press any <ENTER> to exit...')
