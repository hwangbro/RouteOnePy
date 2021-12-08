from dataclasses import dataclass
from stat_modifier import StatModifier

from ivs import IVs, ivs_from_hex

@dataclass
class FightVariation:
    '''Represents set of data required for fight variation calculations'''
    name: str
    att_mod: StatModifier = StatModifier()
    def_mod: StatModifier = StatModifier()
    ivs: IVs = IVs()
    enemy_ivs: ivs = ivs_from_hex(0x9888)
