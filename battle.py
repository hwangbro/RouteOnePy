from stat_modifier import StatModifier
from damage_calc import DamageCalc, n_shot_with_mods
from pokemon import Pokemon
from fight_variation import FightVariation
from move import Move

from dataclasses import dataclass, field
from typing import Any

@dataclass
class SingleBattle:
    """Represents a battle between two pokemon, supplied to DamageCalc"""
    attacker: Pokemon
    defender: Pokemon
    att_mod: StatModifier
    def_mod: StatModifier

    def choose_summary(self, verbosity: int, indent: bool=False) -> str:
        sep = '\n'
        if indent:
            sep = '\n\t'
        ret = ''
        if verbosity == 0:
            pass
        elif verbosity == 1:
            ret = f'{sep}{sep.join(self.short_summary)}'
        elif verbosity == 2:
            ret = f'{sep}{sep.join(self.short_summary)}'
            ret += f'{sep}{sep.join(self.move_summary())}'
            ret += f'\n{sep}{sep.join(self.move_summary(reverse=True))}'
            ret += '\n'
        else:
            raise IndexError(f'Could not parse verbosity level {verbosity}')

        return ret

    @property
    def short_summary(self) -> list[str]:
        '''Returns a shortened summary associated with verbosity = 1'''

        ret = []
        ret.append(f'LVL {self.attacker.level} EXP NEEDED: {self.attacker.exp_to_next_level}/{self.attacker.exp_for_level}')
        line = f'{self.attacker.level_name} vs {self.defender.level_name}'
        line += f'          >>> EXP GIVEN: {self.defender.exp_given()}'
        ret.append(line)
        return ret

    def move_summary(self, reverse: bool=False) -> list[str]:
        '''Returns the extra move summary associated with verbosity = 2

        The reverse parameter is used to switch the attacker and defender to
        print opponent move data
        '''

        ret = []
        attacker, defender, a_mod, d_mod = self.attacker, self.defender, self.att_mod, self.def_mod
        if reverse:
            attacker, defender, a_mod, d_mod = self.defender, self.attacker, self.def_mod, self.att_mod
        x = f'{attacker.name} ({attacker.stats_str})'
        if a_mod.has_bbs or a_mod.has_mods:
            x += f' {a_mod} -> ({a_mod.mod_stats_str(attacker)}'
        ret.append(f'{x}')

        for move in attacker.moveset:
            ret += DamageCalc(move, attacker, defender, a_mod, d_mod).summary
        return ret

@dataclass
class Battle:
    """"Represents a battle between you and a trainer/wild"""
    pokemon: Pokemon
    opponent: Any # Union[Pokemon, Trainer]
    variations: dict[str, FightVariation] = field(default_factory=dict)
    range_checks: dict[str, dict] = field(default_factory = dict)
    att_mod: StatModifier=StatModifier() # or dict
    def_mod: StatModifier=StatModifier() # or dict
    participants: int=1
    verbosity: int=1
    wild: bool=False

    def __post_init__(self):
        self.pokes = self.opponent if self.wild else self.opponent.pokes

    def battle(self) -> str:
        """Performs a battle.

        Returns a string summary of the battle based on the verbosity.
        This also automatically perform and print any variation and range
        checks.

        Finally, it will give the correct amount of exp to self.pokemon
        """

        # Fill in the blanks for non-specified modifiers
        for mod in self.att_mod, self.def_mod:
            if isinstance(mod, dict):
                for idx in range(len(self.pokes)):
                    if idx+1 not in mod:
                        mod[idx+1] = StatModifier()

        # Convert all single-specified data to dictionaries per pokemon index
        if self.wild:
            self.pokes = {1: self.pokes}
        if isinstance(self.pokes, list):
            self.pokes = {idx+1: p for idx, p in enumerate(self.pokes)}
        if isinstance(self.att_mod, StatModifier):
            self.att_mod = {idx: self.att_mod for idx in range(1, len(self.pokes) + 1)}
        if isinstance(self.def_mod, StatModifier):
            self.def_mod = {idx: self.def_mod for idx in range(1, len(self.pokes) + 1)}

        ret = ''
        orig_ivs = self.pokemon.ivs
        combined = {idx: (self.pokes[idx], self.att_mod[idx], self.def_mod[idx])
                    for idx in self.pokes}


        for idx, (poke, a_mod, d_mod) in combined.items():
            orig_wild_ivs = poke.ivs
            # main battle
            single_battle = SingleBattle(self.pokemon, poke, a_mod, d_mod)
            ret += f'{single_battle.choose_summary(self.verbosity)}'

            # Process variations
            fights: dict[str,str] = {}
            if idx in self.variations:
                for name, v in self.variations[idx].items():
                    fight = self.parse_single_battle(v, poke)
                    fights[name] = fight.choose_summary(self.verbosity, True)

            if 'all' in self.variations:
                for name, v in self.variations['all'].items():
                    fight = self.parse_single_battle(v, poke)
                    fights[name] = fight.choose_summary(self.verbosity, True)

            # Process range checks
            range_checks = {}
            rc_data = {}
            if idx in self.range_checks:
                for name, rc in self.range_checks[idx].items():
                    turns = rc['turns']
                    if isinstance(rc['moves'], Move):
                        rc['moves'] = [rc['moves']] * turns
                    if isinstance(rc['att_mods'], StatModifier):
                        rc['att_mods'] = [rc['att_mods']] * turns
                    if isinstance(rc['def_mods'], StatModifier):
                        rc['def_mods'] = [rc['def_mods']] * turns
                    range_checks[name] = n_shot_with_mods(
                        attacker=self.pokemon,
                        defender=poke,
                        turns=rc['turns'],
                        moves=rc['moves'],
                        att_mods=rc['att_mods'],
                        def_mods=rc['def_mods']
                    )
                    rc_data[name] = rc

            for name, fight in fights.items():
                ret += f'\nVariation {name}:\n{fight}'

            rcs = ''
            for name, rc in range_checks.items():
                rcs += f'\nRange Check {name}: {rc:.5f}%'
                for turn in range(rc_data[name]['turns']):
                    rcs += f'\n\tTurn #{turn+1}: '
                    rcs += f'Move: {rc_data[name]["moves"][turn].name}'
                    rcs += f'\n\t\tatt_mod: {rc_data[name]["att_mods"][turn]}'
                    rcs += f'\n\t\tdef_mod: {rc_data[name]["def_mods"][turn]}'
            if rcs:
                ret += rcs + '\n\n'

            # Reset IVs in between each fight
            if poke.ivs != orig_wild_ivs:
                poke.ivs = orig_wild_ivs
                poke.calculate_stats()
            if self.pokemon.ivs != orig_ivs:
                self.pokemon.ivs = orig_ivs
                self.pokemon.calculate_stats()

            poke.battle(self.pokemon, self.participants)

        ret = ret.strip()

        if self.verbosity:
            details = f'{self.opponent.level_name}' if self.wild else f'{self.opponent}'
            ret = f'\n{details}\n{ret}\n\n'
        return ret

    def parse_single_battle(self, variation: FightVariation, poke: Pokemon) -> SingleBattle:
        '''Recalculates stats and returns a SingleBattle struct'''

        self.pokemon.ivs = variation.ivs
        self.pokemon.calculate_stats()
        poke.ivs = variation.enemy_ivs
        poke.calculate_stats()
        return SingleBattle(self.pokemon, poke, variation.att_mod, variation.def_mod)
