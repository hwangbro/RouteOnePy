from dataclasses import dataclass
from move import Move

@dataclass
class TrainerClass:
    name: str
    base_money: int

@dataclass
class Trainer:
    trainer_class: TrainerClass
    pokes: list
    offset: int
    alias: str=''

    @property
    def poke_list(self) -> str:
        '''Returns the party string of a trainer'''
        return ', '.join([f'L{pokemon.level} {pokemon.name}' for pokemon in self.pokes])

    @property
    def prize_money(self) -> int:
        '''Returns prize money'''
        last_poke_lvl = self.pokes[-1].level
        return self.trainer_class.base_money * last_poke_lvl

    def set_move(self, poke_index: int, move_index: int, move: Move, is_yellow: bool=True) -> None:
        '''Sets the move of a pokemon given the party index and move index

        Move object is expected, not a string. For backwards compatability,
        yellow uses a different indexing system
        '''

        if is_yellow:
            poke_index -= 1
            move_index -= 1
        if move_index >= len(self.pokes[poke_index].moveset):
            self.pokes[poke_index].moveset.add_move(move)
        else:
            self.pokes[poke_index].moveset.set_move(move_index, move)

    def __eq__(self, other) -> bool:
        return isinstance(other, Trainer) and self.offset == other.offset

    def __repr__(self) -> str:
        alias_str = ''
        # Don't add the alias to the repr when it matches the class
        # e.g. trainer class "LANCE" = alias "LANCE"
        if self.alias and self.alias.lower() != self.trainer_class.name.lower():
            alias_str = f' ({self.alias})'
        return f'{self.trainer_class.name}{alias_str} ({hex(self.offset)}: {self.poke_list}) Prize {self.prize_money}'
