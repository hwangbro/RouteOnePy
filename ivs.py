from dataclasses import dataclass

@dataclass
class IVs:
    attack: int = 9
    defense: int = 8
    speed: int = 8
    special: int = 8
    hp: int = 8

    def __post_init__(self):
        self.hp = (((self.attack & 1) << 3) +
        ((self.defense & 1) << 2) +
        ((self.speed & 1) << 1) +
        (self.special & 1))

    @property
    def hex(self) -> int:
        '''Return hex value of IVs'''
        return (self.attack << 12) | (self.defense << 8) | (self.speed << 4) | (self.special)

def ivs_from_hex(ivs) -> IVs:
    '''Returns IVs object from hex value'''
    attack = ivs >> 12 & 15
    defense = ivs >> 8 & 15
    speed = ivs >> 4 & 15
    special = ivs & 15
    return IVs(attack, defense, speed, special)
