from enum import Enum, auto

class ExpCurve(Enum):
    Slow = auto()
    Medium_Slow = auto()
    Medium = auto()
    Fast = auto()
    Null = auto()

    def exp_for_level(self, level: int) -> int:
        '''Returns exp needed to get from one level to the next

        Assumes you start with fresh exp on the previous level, as if you
        used a rare candy
        '''
        return self.lowest_exp_for_level(level+1) - self.lowest_exp_for_level(level)

    def lowest_exp_for_level(self, level: int) -> int:
        '''Internal calculation for exp-curve adjusted level requirements'''
        exp = 0
        if self == ExpCurve.Slow:
            exp = 5 * pow(level, 3) / 4
        elif self == ExpCurve.Medium_Slow:
            exp = (6 * pow(level, 3) / 5) - (15 * pow(level, 2)) + 100 * level - 140
        elif self == ExpCurve.Medium:
            exp = pow(level, 3)
        elif self == ExpCurve.Fast:
            exp = 4 * pow(level, 3) / 5
        return int(exp)

    def exp_to_next_lvl(self, level: int, total_exp: int) -> int:
        '''Returns exp needed for next level given the total exp collected'''
        return self.lowest_exp_for_level(level+1) - total_exp
