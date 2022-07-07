from move import Move
from pokemon import Pokemon
from stat_modifier import StatModifier
from type import apply_effectiveness

from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar, Tuple
from itertools import product


@dataclass
class BattleVars:
    """Represents variables needed for a single roll calculation"""
    move: Move
    att_mod: StatModifier
    def_mod: StatModifier
    min_nc: int
    min_c: int
    max_nc: int
    max_c: int
    prob_nc: Tuple
    prob_c: Tuple
    crit_chance: int

@dataclass
class DamageCalc:
    """Represents a single damage calculation"""
    move: Move
    attacker: Pokemon
    defender: Pokemon
    att_mod: StatModifier
    def_mod: StatModifier

    MIN_RANGE: ClassVar[int] = 217
    MAX_RANGE: ClassVar[int] = 255

    def damage(self, range_roll: int, crit: bool=False) -> int:
        '''Passthrough call to _damage'''
        return _damage(self.move, self.attacker, self.defender,
                            self.att_mod, self.def_mod, range_roll, crit)

    def min_damage(self, crit=False) -> int:
        return self.damage(self.MIN_RANGE, crit)

    def max_damage(self, crit=False) -> int:
        return self.damage(self.MAX_RANGE, crit)

    def one_shot_percent(self, crit: bool=False) -> float:
        range_roll = self.MIN_RANGE
        while self.damage(range_roll, crit) < self.defender._hp:
            range_roll += 1

        return 100 * (self.MAX_RANGE - range_roll + 1) / (self.MAX_RANGE - self.MIN_RANGE + 1)

    @property
    def summary(self) -> list[str]:
        '''Returns the battle summary of a particular move

        Return value is a list of strings for ease of formatting
        '''
        ret = []

        line = f'{self.move.name}'
        max_dmg = self.max_damage()
        max_crit_dmg = self.max_damage(True)

        min_dmg = self.min_damage()
        min_crit_dmg = self.min_damage(True)

        if max_dmg == 0 and max_crit_dmg == 0:
            return [line]

        if max_dmg:
            line += f' {min_dmg}-{max_dmg}'

        line += '\t(crit: '

        line += f'{min_crit_dmg}-{max_crit_dmg})'
        ret.append(line)

        dmg_rolls, crit_dmg_rolls = _range_rolls(
            move=self.move,
            attacker=self.attacker,
            defender=self.defender,
            att_mod=self.att_mod,
            def_mod=self.def_mod
        )

        for name, rolls in zip(['Normal', 'Crit'], [dmg_rolls, crit_dmg_rolls]):
            line = f'\t{name} rolls: '
            for roll, frequency in rolls.items():
                line += f'{roll}x{frequency}, '
            line = line.strip(', ')
            ret.append(line)

        for hits in range(1, 9):
            kill_pct = n_shot_with_mods(self.attacker, self.defender, hits, self.move, self.att_mod, self.def_mod, True)

            if kill_pct >= 1 and kill_pct <= 99.999:
                ret.append(f'\t(Overall {hits}-hit Kill%: {kill_pct:.4f}%)')
        return ret

def n_shot_with_mods(attacker: Pokemon,
                     defender: Pokemon,
                     turns: int,
                     moves: Move,
                     att_mods: StatModifier,
                     def_mods: StatModifier,
                     repeat: bool=False
    ) -> float:
    '''Returns the probability of an n-hit kill%'''

    if isinstance(moves, Move):
        moves = [moves] * turns
    if isinstance(att_mods, StatModifier):
        att_mods = [att_mods] * turns
    if isinstance(def_mods, StatModifier):
        def_mods = [def_mods] * turns

    if len(moves) != turns:
        raise ValueError('Wrong number of turns')
    if len(att_mods) != turns:
        raise ValueError('Wrong number of attack mods')
    if len(def_mods) != turns:
        raise ValueError('Wrong number of defense mods')

    current_min = 0
    current_max = 0

    turn_dict = {}
    turn_data= []

    for move, att_mod, def_mod in zip(moves, att_mods, def_mods):
        # Utilize memoization
        if data := turn_dict.get((move, att_mod, def_mod)):
            turn_data.append(data)
            continue

        _min_nc = _damage(move, attacker, defender, att_mod, def_mod, 217, False)
        _min_c = _damage(move, attacker, defender, att_mod, def_mod, 217, True)
        _max_nc = _damage(move, attacker, defender, att_mod, def_mod, 255, False)
        _max_c = _damage(move, attacker, defender, att_mod, def_mod, 255, True)

        p_nc, p_c = _range_prob_rolls(
            move=move,
            attacker=attacker,
            defender=defender,
            att_mod=att_mod,
            def_mod=def_mod
        )

        if move.name.lower() in {'crabhammer', 'karate chop', 'razor leaf', 'slash'}:
            crit_chance = min(attacker.species.base_spd * 4, 255) / 256
        else:
            crit_chance = (attacker.species.base_spd // 2) / 256

        turn = BattleVars(move, att_mod, def_mod, _min_nc, _min_c,
                        _max_nc, _max_c, p_nc, p_c, crit_chance)

        # Memoization
        turn_data.append(turn)
        turn_dict[(move, att_mod, def_mod)] = turn

    for turn in turn_data:
        current_max += max(turn.max_nc, turn.max_c)
        current_min += min(turn.min_nc, turn.min_c)

    # Not a range, return 100 or 0
    if current_min >= defender._hp:
        return 100
    if current_max < defender._hp:
        return 0

    # Generate all permutation of crits
    crits = list(product([True, False], repeat=turns))
    chances = 0

    turn_zero = turn_data[0]

    results_dict = defaultdict(float)
    for crit_combo in crits:
        crit_chance = 1
        crit_combo_chance = 0
        num_crits = crit_combo.count(True)

        # If repeat, order doesn't matter and we can use combinations
        if repeat and num_crits in results_dict:
            chances += results_dict[num_crits]
            continue

        for idx, move in enumerate(crit_combo):
            crit_rate = turn_data[idx].crit_chance
            crit_chance *= crit_rate if move else 1-crit_rate

        if crit_combo[0]:
            bottom_range, top_range = (turn_zero.min_c, turn_zero.max_c+1)
        else:
            bottom_range, top_range = (turn_zero.min_nc, turn_zero.max_nc+1)

        for i in range(bottom_range, top_range):
            x = _n_shot_percent_inner(
                hp = defender._hp,
                all_turn_data=turn_data,
                stacked_dmg=0,
                rolled_dmg=i,
                crits=crit_combo,
                current_turn=0
            )
            crit_combo_chance += x * crit_chance
        chances += crit_combo_chance
        results_dict[num_crits] = crit_combo_chance
    return 100 * chances / pow(39, turns)

def _n_shot_percent_inner(
    hp: int,
    all_turn_data: list[BattleVars],
    stacked_dmg: int,
    rolled_dmg: int,
    crits: Tuple[int,],
    current_turn: int
) -> float:
    '''Inner function handling more calculations

    Calculates a single roll, calls itself recursively for future turns
    '''

    num_turns = len(all_turn_data)
    t_data = all_turn_data[current_turn]

    crit = crits[current_turn]
    stacked_dmg += rolled_dmg
    remaining_min_dmg = 0
    remaining_max_dmg = 0
    prob_c_min = t_data.prob_c[rolled_dmg - t_data.min_c]
    prob_nc_min = t_data.prob_nc[rolled_dmg - t_data.min_nc]

    for i in range(current_turn+1, num_turns):
        if crits[i]:
            remaining_max_dmg += all_turn_data[i].max_c
            remaining_min_dmg += all_turn_data[i].min_c
        else:
            remaining_max_dmg += all_turn_data[i].max_nc
            remaining_min_dmg += all_turn_data[i].min_nc

    if stacked_dmg >= hp or (stacked_dmg + remaining_min_dmg) >= hp:
        ret = pow(39, num_turns - (current_turn + 1))
        if crit:
            ret *= prob_c_min
        else:
            ret *= prob_nc_min
        return ret
    elif (current_turn >= num_turns - 1) or (stacked_dmg + remaining_max_dmg < hp):
        return 0
    else:
        current_turn += 1
        t_data = all_turn_data[current_turn]
        chances = 0
        bottom, top = t_data.min_nc, t_data.max_nc + 1

        if crits[current_turn]:
            bottom, top = t_data.min_c, t_data.max_c+1

        for i in range(bottom, top):
            x = _n_shot_percent_inner(
                all_turn_data=all_turn_data,
                hp=hp,
                stacked_dmg=stacked_dmg,
                rolled_dmg=i,
                crits=crits,
                current_turn=current_turn
            )
            chances += x
        return chances * prob_c_min if crit else chances * prob_nc_min

def _range_rolls(move: Move,
                 attacker: Pokemon,
                 defender: Pokemon,
                 att_mod: StatModifier,
                 def_mod: StatModifier
    ) -> Tuple[dict[int, int], dict[int, int]]:
    '''Returns two dictionaries (non-crit and crit) of rolls and damages'''

    dmg_rolls = defaultdict(int)
    crit_dmg_rolls = defaultdict(int)

    for roll in range(217, 256):
        for crit in (False, True):
            dmg = _damage(move, attacker, defender, att_mod, def_mod, roll, crit)
            if dmg > defender._hp:
                dmg = defender._hp
            if crit:
                crit_dmg_rolls[dmg] += 1
            else:
                dmg_rolls[dmg] += 1

    return dmg_rolls, crit_dmg_rolls

def _range_prob_rolls(move: Move,
                      attacker: Pokemon,
                      defender: Pokemon,
                      att_mod: StatModifier,
                      def_mod: StatModifier
    ) -> Tuple[dict[int, int], dict[int, int]]:
    '''
    Returns two dictionaries (non-crit and crit) of damage rolls and
    the associated probabilities
    '''

    probs_nc = defaultdict(int)
    probs_c = defaultdict(int)

    dmg_rolls, crit_dmg_rolls = _range_rolls(move, attacker, defender,
                                             att_mod, def_mod)
    min_dmg = min(dmg_rolls.keys())
    min_crit_dmg = min(crit_dmg_rolls.keys())

    for roll, freq in dmg_rolls.items():
        probs_nc[roll - min_dmg] = freq
    for roll, freq in crit_dmg_rolls.items():
        probs_c[roll - min_crit_dmg] = freq

    return probs_nc, probs_c

def _damage(move: Move,
            attacker: Pokemon,
            defender: Pokemon,
            att_mod: StatModifier,
            def_mod: StatModifier,
            roll: int,
            crit: bool=False
    ) -> int:
    '''Core damage calculation

    For a given roll, performs the correct damage calculation for a move. This
    function handles all damage calculations, including type effectiveness,
    STAB, and crits
    '''

    if move.name.lower() == 'night shade':
        return attacker.level

    if move.power <= 0:
        return 0

    # limit roll to 217-255
    roll = max(roll, 217)
    roll = min(roll, 255)

    att_stat = attacker._att if crit else att_mod.mod_att(attacker)
    def_stat = defender._def if crit else def_mod.mod_def(defender)
    if move.type.special:
        att_stat = attacker._spc if crit else att_mod.mod_spc(attacker)
        def_stat = defender._spc if crit else def_mod.mod_spc(defender)

    if move.name.lower() in {'selfdestruct', 'explosion'}:
        def_stat = max(def_stat // 2, 1)

    stab = move.type in {attacker.species.type1, attacker.species.type2}
    level = attacker.level
    if crit:
        level *= 2
    level %= 256

    dmg = (level * 2 // 5) + 2
    dmg *= att_stat
    dmg *= move.power
    dmg //= 50
    dmg //= def_stat
    dmg += 2
    if stab:
        dmg = dmg * 3 // 2
    dmg = apply_effectiveness(
        damage=dmg,
        att_type=move.type,
        def_type=defender.species.type1,
        def_type2=defender.species.type2
    )

    if dmg == 0:
        return 0

    dmg *= roll
    dmg //= 255
    return max(int(dmg), 1)
