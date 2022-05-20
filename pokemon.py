from dataclasses import dataclass, field
from math import ceil, sqrt

from species import Species
from ivs import IVs, ivs_from_hex
from moveset import Moveset, get_default_moveset
import data

@dataclass
class Pokemon:
    species: str
    level: int
    ivs: IVs = IVs()
    wild: bool = False
    game: str = 'rb'
    moveset: Moveset = field(default_factory=Moveset)

    def __post_init__(self):
        # Allow initialization of Pokemon with species names
        if isinstance(self.species, str):
            self.species = data.get_species(self.species)
            if not self.species:
                raise ValueError('Could not find valid species')

        # If no moveset is supplied, grab the default learnset
        # Slightly expensive operation to grab learnset data every time
        if not self.moveset:
            learnset = data.get_learnset(self.species.dex_num, self.game)
            self.moveset = get_default_moveset(learnset, self.level)

        self.ev_hp = 0
        self.ev_att = 0
        self.ev_def = 0
        self.ev_spd = 0
        self.ev_spc = 0
        self._hp = self._att = self._def = self._spd = self._spc = 0
        self.att_badge = self.def_badge = self.spd_badge = self.spc_badge = False
        self.boosted_exp = False
        self.total_exp = 0
        self._update_exp()
        self.calculate_stats()

    @property
    def attack(self) -> int:
        '''Returns attack stat'''
        return 9 * self._att // 8 if self.att_badge else self._att

    @property
    def defense(self) -> int:
        '''Returns defense stat'''
        return 9 * self._def // 8 if self.def_badge else self._def

    @property
    def speed(self) -> int:
        '''Returns speed stat'''
        return 9 * self._spd // 8 if self.spd_badge else self._spd

    @property
    def special(self) -> int:
        '''Returns special stat'''
        return 9 * self._spc // 8 if self.spc_badge else self._spc

    @property
    def name(self) -> str:
        '''Passthrough for species name'''
        return self.species.name

    @property
    def level_name(self) -> str:
        '''Returns name in the form <L## NAME>'''
        return f'L{self.level} {self.name}'

    @property
    def stats_str(self) -> str:
        '''Returns stats formatted as hp/att/def/spd/spc'''
        return f'{self._hp}/{self.attack}/{self.defense}/{self.speed}/{self.special}'

    def battle(self, winner, participants: int=1) -> None:
        '''Performs exp/stat calculations for a battle

        This function is expected to be called by enemy pokemon with your
        own pokemon supplied as a parameter
        '''

        if participants:
            winner.gain_stat_exp(self.species, participants)
            winner.gain_exp(self.exp_given(participants))

    def calculate_stats(self) -> None:
        '''Recalculates stats based on IVs and EVs

        underscore variables represent "raw" stat data that is sometimes
        called directly for damage calculations
        '''
        self._hp = self._calculate_stat_with_iv(self.ivs.hp, self.species.base_hp, self.ev_hp, True)
        self._att = self._calculate_stat_with_iv(self.ivs.attack, self.species.base_att, self.ev_att)
        self._def = self._calculate_stat_with_iv(self.ivs.defense, self.species.base_def, self.ev_def)
        self._spd = self._calculate_stat_with_iv(self.ivs.speed, self.species.base_spd, self.ev_spd)
        self._spc = self._calculate_stat_with_iv(self.ivs.special, self.species.base_spc, self.ev_spc)

    def _calculate_stat_with_iv(self, iv: int, base: int, ev: int, hp=False) -> int:
        '''Recalculates the stat value given IVs and EVs'''
        x = calculate_stat_numerator(iv, base, ev) * self.level // 100
        x += 5
        if hp:
            x += self.level + 5
        return x

    def _update_exp(self) -> None:
        '''Updates EXP values'''
        self.total_exp = self.species.exp_curve.lowest_exp_for_level(self.level)

    @property
    def exp_to_next_level(self) -> int:
        '''Passthrough to exp_curve.exp_to_next_lvl'''
        return self.species.exp_curve.exp_to_next_lvl(self.level, self.total_exp)

    @property
    def exp_for_level(self) -> int:
        '''total exp needed to get from this level to the next (no partial exp)'''
        return self.species.exp_curve.exp_for_level(self.level)

    def exp_given(self, participants: int=1) -> int:
        '''Returns how much exp this pokemon gives if it is beaten in battle'''
        x = self.species.kill_exp // participants
        x *= self.level
        x = x // 7
        x *= 3
        if self.wild:
            x = x // 3
        else:
            x = x // 2
        return x

    def gain_exp(self, exp: int) -> None:
        '''Adds exp to itself and recalculates stats'''
        e = exp
        if self.boosted_exp:
            e = e * 3 // 2

        self.total_exp += e

        while self.exp_to_next_level <= 0 and self.level < 100:
            self.level += 1
            self.calculate_stats()

    def gain_stat_exp(self, species: Species, participants: int=1) -> None:
        '''Recalculates EVs'''
        self.ev_hp += species.base_hp // participants
        self.ev_hp = cap_ev(self.ev_hp)
        self.ev_att += species.base_att // participants
        self.ev_att = cap_ev(self.ev_att)
        self.ev_def += species.base_def // participants
        self.ev_def = cap_ev(self.ev_def)
        self.ev_spd += species.base_spd // participants
        self.ev_spd = cap_ev(self.ev_spd)
        self.ev_spc += species.base_spc // participants
        self.ev_spc = cap_ev(self.ev_spc)

    def use_candy(self) -> None:
        '''Uses a candy and recalculates exp/stats'''
        if self.level != 100:
            self.level += 1
            self._update_exp()
            self.calculate_stats()

    def use_vitamin(self, vitamin_name: str) -> None:
        '''Uses vitamins and recalculates stats'''
        if vitamin_name == 'PROTEIN':
            self._use_vitamin('att')
        elif vitamin_name == 'IRON':
            self._use_vitamin('def')
        elif vitamin_name == 'CARBOS':
            self._use_vitamin('spd')
        elif vitamin_name == 'CALCIUM':
            self._use_vitamin('spc')
        elif vitamin_name == 'HP UP':
            self._use_vitamin('hp')

    def _use_vitamin(self, stat: str):
        '''Uses vitamins

        Stats is expected to be hp/att/def/spd/spc
        This function is a bit hacky and refers to __dict__ to reference
        the variable directly
        '''
        stat = f'ev_{stat}'
        stat_val = self.__dict__[stat]
        if stat_val < 25600:
            self.__dict__[stat] += 2560
            self.calculate_stats()

    def evolve(self, species: str) -> None:
        '''Transforms self into the supplied species

        Currently a bit hacky and does not validate whether the evolution is
        actually possible
        '''
        self.species = data.get_species(species)
        self.calculate_stats()

    def print_possible_stats(self) -> str:
        '''Returns possible stat variations with different IVs'''
        possible_hps = [self._calculate_stat_with_iv(iv, self.species.base_hp, self.ev_hp, True) for iv in range(16)]
        possible_atts = [self._calculate_stat_with_iv(iv, self.species.base_att, self.ev_att) for iv in range(16)]
        possible_defs = [self._calculate_stat_with_iv(iv, self.species.base_def, self.ev_def) for iv in range(16)]
        possible_spds = [self._calculate_stat_with_iv(iv, self.species.base_spd, self.ev_spd) for iv in range(16)]
        possible_spcs = [self._calculate_stat_with_iv(iv, self.species.base_spc, self.ev_spc) for iv in range(16)]

        ret = f'L{self.level} {self.name}\n'
        ret += 'Stat ranges WITHOUT badge boosts:\n'
        ret += 'IV  |0   |1   |2   |3   |4   |5   |6   |7   |8   |9   |10  |11  |12  |13  |14  |15\n'
        ret += '------------------------------------------------------------------------------------\n'

        hp_line = att_line = def_line = spd_line = spc_line = ''
        for idx in range(16):
            hp_line += f'|{str(possible_hps[idx]).rjust(4)}'
            att_line += f'|{str(possible_atts[idx]).rjust(4)}'
            def_line += f'|{str(possible_defs[idx]).rjust(4)}'
            spd_line += f'|{str(possible_spds[idx]).rjust(4)}'
            spc_line += f'|{str(possible_spcs[idx]).rjust(4)}'

        ret += f'HP  {hp_line}\n'
        ret += f'ATT {att_line}\n'
        ret += f'DEF {def_line}\n'
        ret += f'SPD {spd_line}\n'
        ret += f'SPC {spc_line}\n'
        return ret

    def set_iv(self, iv: int) -> None:
        '''Setter for IVs and recalculates stats'''
        self.ivs = ivs_from_hex(iv)
        self.calculate_stats()

    def set_all_badges(self, value: bool=True) -> None:
        '''Easily set all badge boosts'''
        self.att_badge = self.def_badge = self.spd_badge = self.spc_badge = value

def cap_ev(ev: int) -> int:
    '''Easy way to cap EVs to 65535'''
    return min(ev, 65535)

def ev_calc(ev: int) -> int:
    '''Calculates EVs'''
    return min(ceil(sqrt(ev)), 255) // 4

def calculate_stat_numerator(iv: int, base: int, ev: int) -> int:
    '''Used for stat calculations'''
    return 2 * (iv + base) + ev_calc(ev)
