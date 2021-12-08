from dataclasses import dataclass
from type import Type

@dataclass
class Move:
    name: str
    type: Type
    pp: int
    power: int
    accuracy: int
    index: int

    def __hash__(self):
        return hash((self.name, self.index))

@dataclass
class LevelMove:
    level: int
    move: Move
