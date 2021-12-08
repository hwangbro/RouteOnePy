from enum import Enum
from dataclasses import dataclass

class Effectiveness(Enum):
    NoEffect = 0
    VeryWeak = 0.25
    Weak = 0.5
    Normal = 1
    SuperEffective = 2
    SuperSuperEffective = 4

class Type(Enum):
    Null = -1
    Normal = 0
    Fighting = 1
    Flying = 2
    Poison = 3
    Ground = 4
    Rock = 5
    Bug = 6
    Ghost = 7
    Fire = 8
    Water = 9
    Grass = 10
    Electric = 11
    Psychic = 12
    Ice = 13
    Dragon = 14

    @property
    def physical(self) -> bool:
        return self.value >= self.Normal.value and self.value <= self.Ghost.value

    @property
    def special(self) -> bool:
        return not self.physical

    def __repr__(self) -> str:
        return self.name

@dataclass
class TypeEffectiveness:
    att_type: Type
    def_type: Type

    @property
    def effectiveness(self) -> Effectiveness:
        '''Returns the Effectiveness relationship between its two types'''
        return effectiveness(self.att_type, self.def_type)

    def __repr__(self) -> str:
        return f'{self.att_type} - {self.def_type}: {self.effectiveness}'


def effectiveness(att_type: Type, def_type1: Type, def_type2: Type=Type.Null) -> Effectiveness:
    '''
    Given attacking type and both defending types,
    return the correct damage multiplier
    '''
    return Effectiveness(_effectiveness(att_type, def_type1) * _effectiveness(att_type, def_type2))

def _effectiveness(att_type: Type, def_type: Type) -> int:
    '''Return the multiplier of two types'''
    if Type.Null in (att_type, def_type):
        return 1
    return type_table[att_type.value][def_type.value]

def apply_effectiveness(damage: int, att_type: Type, def_type: Type, def_type2: Type = Type.Null) -> int:
    '''Apply damage calculations given both defensive types'''
    for e in effect_list:
        if e.att_type == att_type:
            if e.def_type in (def_type, def_type2):
                damage *= e.effectiveness.value
    return damage

type_table = [
    [1, 1, 1, 1, 1, 0.5, 1, 0, 1, 1, 1, 1, 1, 1, 1],           # Normal
    [2, 1, 0.5, 0.5, 1, 2, 0.5, 0, 1, 1, 1, 1, 0.5, 2, 1],     # Fighting
    [1, 2, 1, 1, 1, 0.5, 2, 1, 1, 1, 2, 0.5, 1, 1, 1],         # Flying
    [1, 1, 1, 0.5, 0.5, 0.5, 2, 0.5, 1, 1, 2, 1, 1, 1, 1],     # Poison
    [1, 1, 0, 2, 1, 2, 0.5, 1, 2, 1, 0.5, 2, 1, 1, 1],         # Ground
    [1, 0.5, 2, 1, 0.5, 1, 2, 1, 2, 1, 1, 1, 1, 2, 1],         # Rock
    [1, 0.5, 0.5, 2, 1, 1, 1, 0.5, 0.5, 1, 2, 1, 2, 1, 1],     # Bug
    [0, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0, 1, 1],             # Ghost
    [1, 1, 1, 1, 1, 0.5, 2, 1, 0.5, 0.5, 2, 1, 1, 2, 0.5],     # Fire
    [1, 1, 1, 1, 2, 2, 1, 1, 2, 0.5, 0.5, 1, 1, 1, 0.5],       # Water
    [1, 1, 0.5, 0.5, 2, 2, 0.5, 1, 0.5, 2, 0.5, 1, 1, 1, 0.5], # Grass
    [1, 1, 2, 1, 0, 1, 1, 1, 1, 2, 0.5, 0.5, 1, 1, 0.5],       # Electric
    [1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 1, 1],           # Psychic
    [1, 1, 2, 1, 2, 1, 1, 1, 1, 0.5, 2, 1, 1, 0.5, 2],         # Ice
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],             # Dragon
]

effect_list = [
    TypeEffectiveness(Type.Water, Type.Fire),
    TypeEffectiveness(Type.Fire, Type.Grass),
    TypeEffectiveness(Type.Fire, Type.Ice),
    TypeEffectiveness(Type.Grass, Type.Water),
    TypeEffectiveness(Type.Electric, Type.Water),
    TypeEffectiveness(Type.Water, Type.Rock),
    TypeEffectiveness(Type.Ground, Type.Flying),
    TypeEffectiveness(Type.Water, Type.Water),
    TypeEffectiveness(Type.Fire, Type.Fire),
    TypeEffectiveness(Type.Electric, Type.Electric),
    TypeEffectiveness(Type.Ice, Type.Ice),
    TypeEffectiveness(Type.Grass, Type.Grass),
    TypeEffectiveness(Type.Psychic, Type.Psychic),
    TypeEffectiveness(Type.Fire, Type.Water),
    TypeEffectiveness(Type.Grass, Type.Fire),
    TypeEffectiveness(Type.Water, Type.Grass),
    TypeEffectiveness(Type.Electric, Type.Grass),
    TypeEffectiveness(Type.Normal, Type.Rock),
    TypeEffectiveness(Type.Normal, Type.Ghost),
    TypeEffectiveness(Type.Ghost, Type.Ghost),
    TypeEffectiveness(Type.Fire, Type.Bug),
    TypeEffectiveness(Type.Fire, Type.Rock),
    TypeEffectiveness(Type.Water, Type.Ground),
    TypeEffectiveness(Type.Electric, Type.Ground),
    TypeEffectiveness(Type.Electric, Type.Flying),
    TypeEffectiveness(Type.Grass, Type.Ground),
    TypeEffectiveness(Type.Grass, Type.Bug),
    TypeEffectiveness(Type.Grass, Type.Poison),
    TypeEffectiveness(Type.Grass, Type.Rock),
    TypeEffectiveness(Type.Grass, Type.Flying),
    TypeEffectiveness(Type.Ice, Type.Water),
    TypeEffectiveness(Type.Ice, Type.Grass),
    TypeEffectiveness(Type.Ice, Type.Ground),
    TypeEffectiveness(Type.Ice, Type.Flying),
    TypeEffectiveness(Type.Fighting, Type.Normal),
    TypeEffectiveness(Type.Fighting, Type.Poison),
    TypeEffectiveness(Type.Fighting, Type.Flying),
    TypeEffectiveness(Type.Fighting, Type.Psychic),
    TypeEffectiveness(Type.Fighting, Type.Bug),
    TypeEffectiveness(Type.Fighting, Type.Rock),
    TypeEffectiveness(Type.Fighting, Type.Ice),
    TypeEffectiveness(Type.Fighting, Type.Ghost),
    TypeEffectiveness(Type.Poison, Type.Grass),
    TypeEffectiveness(Type.Poison, Type.Poison),
    TypeEffectiveness(Type.Poison, Type.Ground),
    TypeEffectiveness(Type.Poison, Type.Bug),
    TypeEffectiveness(Type.Poison, Type.Rock),
    TypeEffectiveness(Type.Poison, Type.Ghost),
    TypeEffectiveness(Type.Ground, Type.Fire),
    TypeEffectiveness(Type.Ground, Type.Electric),
    TypeEffectiveness(Type.Ground, Type.Grass),
    TypeEffectiveness(Type.Ground, Type.Bug),
    TypeEffectiveness(Type.Ground, Type.Rock),
    TypeEffectiveness(Type.Ground, Type.Poison),
    TypeEffectiveness(Type.Flying, Type.Electric),
    TypeEffectiveness(Type.Flying, Type.Fighting),
    TypeEffectiveness(Type.Flying, Type.Bug),
    TypeEffectiveness(Type.Flying, Type.Grass),
    TypeEffectiveness(Type.Flying, Type.Rock),
    TypeEffectiveness(Type.Psychic, Type.Fighting),
    TypeEffectiveness(Type.Psychic, Type.Poison),
    TypeEffectiveness(Type.Bug, Type.Fire),
    TypeEffectiveness(Type.Bug, Type.Grass),
    TypeEffectiveness(Type.Bug, Type.Fighting),
    TypeEffectiveness(Type.Bug, Type.Flying),
    TypeEffectiveness(Type.Bug, Type.Psychic),
    TypeEffectiveness(Type.Bug, Type.Ghost),
    TypeEffectiveness(Type.Bug, Type.Poison),
    TypeEffectiveness(Type.Rock, Type.Fire),
    TypeEffectiveness(Type.Rock, Type.Fighting),
    TypeEffectiveness(Type.Rock, Type.Ground),
    TypeEffectiveness(Type.Rock, Type.Flying),
    TypeEffectiveness(Type.Rock, Type.Bug),
    TypeEffectiveness(Type.Rock, Type.Ice),
    TypeEffectiveness(Type.Ghost, Type.Normal),
    TypeEffectiveness(Type.Ghost, Type.Psychic),
    TypeEffectiveness(Type.Fire, Type.Dragon),
    TypeEffectiveness(Type.Water, Type.Dragon),
    TypeEffectiveness(Type.Electric, Type.Dragon),
    TypeEffectiveness(Type.Grass, Type.Dragon),
    TypeEffectiveness(Type.Ice, Type.Dragon),
    TypeEffectiveness(Type.Dragon, Type.Dragon)
]
