from dataclasses import dataclass
from pokemon import Pokemon

multipliers = [0.25, 0.28, 0.33, 0.4, 0.5, 0.66,
                   1, 1.5, 2, 2.5, 3, 3.5, 4]

@dataclass
class StatModifier:
    attack: int = 0
    defense: int = 0
    speed: int = 0
    special: int = 0
    accuracy: int = 0
    evasion: int = 0
    used_x_acc: bool = False
    att_bb: int = 0
    def_bb: int = 0
    spd_bb: int = 0
    spc_bb: int = 0

    def __hash__(self):
        return hash((self.attack, self.defense, self.speed, self.special,
                     self.att_bb, self.def_bb, self.spd_bb, self.spc_bb))

    @property
    def has_mods(self) -> bool:
        '''Returns True if any stat stages are applied'''
        return any((self.attack, self.defense, self.speed, self.special,
                         self.accuracy, self.evasion)) or self.used_x_acc

    @property
    def has_bbs(self) -> bool:
        '''Returns True if any badge boosts are applied'''
        return any((self.att_bb, self.def_bb, self.spd_bb, self.spc_bb))

    def mod_att(self, pokemon: Pokemon) -> int:
        '''For a given Pokemon, apply and return the modified Attack stat'''
        raw = max(modify_stat(pokemon._att, self.attack), 1)
        if pokemon.att_badge:
            for _ in range(self.att_bb + 1):
                raw = 9 * raw // 8

        return raw

    def mod_def(self, pokemon: Pokemon) -> int:
        '''For a given Pokemon, apply and return the modified Defense stat'''
        raw = max(modify_stat(pokemon._def, self.defense), 1)
        if pokemon.def_badge:
            for _ in range(self.def_bb + 1):
                raw = 9 * raw // 8

        return raw

    def mod_spd(self, pokemon: Pokemon) -> int:
        '''For a given Pokemon, apply and return the modified Speed stat'''
        raw = max(modify_stat(pokemon._spd, self.speed), 1)
        if pokemon.spd_badge:
            for _ in range(self.spd_bb + 1):
                raw = 9 * raw // 8

        return raw

    def mod_spc(self, pokemon: Pokemon) -> int:
        '''For a given Pokemon, apply and return the modified Special stat'''
        raw = max(modify_stat(pokemon._spc, self.special), 1)
        if pokemon.spc_badge:
            for _ in range(self.spc_bb + 1):
                raw = 9 * raw // 8

        return raw

    def mod_stats_str(self, pokemon: Pokemon) -> str:
        '''For a given Pokemon, return all modified stats formatted'''
        return f'{pokemon._hp}/{self.mod_att(pokemon)}/{self.mod_def(pokemon)}/{self.mod_spd(pokemon)}/{self.mod_spc(pokemon)}'

    def __repr__(self) -> str:
        base = f'+[{self.attack}/{self.defense}/{self.speed}/{self.special}]'
        bb = f'+<{self.att_bb}/{self.def_bb}/{self.spd_bb}/{self.spc_bb}>'

        ret = ''
        if self.has_mods:
            ret += base
        if self.has_bbs:
            ret = ret + ' ' + bb
        if self.used_x_acc:
            ret += ' +X ACC'

        if not ret:
            ret = '<No Stat Modifications>'
        return ret

def stat_multiplier(stage: int) -> float:
    '''Returns the proper multiplier given the stage'''
    return multipliers[bound(stage)+6]

def modify_stat(original: int, stage: int) -> int:
    '''Applies a modification given a stage'''
    return int(original * stat_multiplier(bound(stage)))

def bound(stage: int) -> int:
    '''Bind the stage between -6 and 6'''
    if stage < -6:
        return -6
    elif stage > 6:
        return 6
    return stage

def parse_stat_mod(mod: dict):
    '''Parse a stat modifier from yaml

    Input can be a dictionary of stat modifier data, or have keys specific
    to pokemon. For the first case, this stat modifier only represents one
    StatModifier object, so we can parse it easily. The second case, we return
    a dictionary with keys being pokemon party index, values being
    StatModifiers
    '''

    if not mod:
        return StatModifier()
    elif any(isinstance(x, int) for x in mod.keys()):
        if not all(isinstance(x, int) for x in mod.keys()):
            raise IndexError(f'If specifying pokemon index for Stat Modifiers, they must all be specified.')
        mods = {}
        for idx, modifier in mod.items():
            mods[idx] = parse_stat_mod_dict(modifier)
        return mods
    elif isinstance(mod, dict):
        return parse_stat_mod_dict(mod)
    raise TypeError(f'Invalid input for stat modifier: {mod}')

def parse_stat_mod_dict(mod_dict: dict) -> StatModifier:
    '''Given a singular stat modifier dictionary, return a StatModifier'''
    stages = mod_dict.get('stages', '0/0/0/0')
    attack, defense, speed, special = [int(stage) for stage in stages.split('/')]
    bbs = mod_dict.get('bbs', '0/0/0/0')
    att_bb, def_bb, spd_bb, spc_bb = [int(bb) for bb in bbs.split('/')]
    return StatModifier(attack, defense, speed, special,
                        att_bb=att_bb, def_bb=def_bb, spd_bb=spd_bb, spc_bb=spc_bb)

def parse_stat_mod_range_checks(mod: dict, turns) -> list[StatModifier]:
    '''Return a list of stat modifiers representing different turns'''
    _stages = mod.get('stages', '0/0/0/0')
    stages = []
    for stage_turn in _stages.split(','):
        attack, defense, speed, special = [int(stage) for stage in stage_turn.split('/')]
        stages.append((attack, defense, speed, special))
    if len(stages) != turns:
        if len(stages) == 1:
            stages = stages * turns
        else:
            raise IndexError(f'Invalid input for number of stages given ({len(stages)} and turns ({turns})')

    _bbs = mod.get('bbs', '0/0/0/0')
    bbs = []
    for bbs_turn in _bbs.split(','):
        att_bb, def_bb, spd_bb, spc_bb = [int(bb) for bb in bbs_turn.split('/')]
        bbs.append((att_bb, def_bb, spd_bb, spc_bb))

    if len(bbs) != turns:
        if len(bbs) == 1:
            bbs = bbs * turns
        else:
            raise IndexError(f'Invalid input for number of bbs given ({len(bbs)} and turns ({turns})')

    ret = []
    for stage, bb in zip(stages, bbs):
        ret.append(StatModifier(
            attack=stage[0],
            defense=stage[1],
            speed=stage[2],
            special=stage[3],
            att_bb=bb[0],
            def_bb=bb[1],
            spd_bb=bb[2],
            spc_bb=bb[3],
        ))

    return ret
