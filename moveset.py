from move import Move

class Moveset(list):
    def set_move(self, move_slot: int, move: Move) -> None:
        '''Sets a moveset index slot to a move

        If the slot specified is less than the current number of moves, append
        the move to the end of the current moveset instead
        '''

        if len(self) > move_slot:
            self[move_slot] = move
        else:
            self.append(move)

    def add_move(self, move: Move) -> None:
        '''Adds a move to the moveset'''
        if move not in self:
            self.append(move)

    def delete_move(self, move: Move) -> None:
        '''Removes a move from the moveset'''
        if move in self:
            self.remove(move)

    def __repr__(self) -> str:
        return ', '.join([x.name for x in self])

def get_default_moveset(learnset: list, level: int) -> Moveset:
    '''Returns the 4 most recently learned moves for a pokemon of this level'''
    moveset = [move.move for move in learnset if move.level <= level]
    if len(moveset) > 4:
        return Moveset(moveset[-4:])
    return Moveset(moveset)
