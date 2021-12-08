from dataclasses import dataclass

from exp_curve import ExpCurve
from type import Type

@dataclass
class Species:
    name: str
    exp_curve: ExpCurve
    type1: Type
    type2: Type
    base_hp: int
    base_att: int
    base_def: int
    base_spd: int
    base_spc: int
    kill_exp: int
    dex_num: int
