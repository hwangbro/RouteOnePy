from constants import *
from type import Type
from species import Species
from trainers import TrainerClass, Trainer
from item import Item
from move import Move, LevelMove
from moveset import get_default_moveset
import pokemon

from typing import Tuple

def get_trainer_classes() -> dict[str, TrainerClass]:
    '''Grabs trainer classes from constants.py'''
    return {name.upper(): TrainerClass(name, money) for name, money in TRAINER_DATA}

def get_items() -> dict[str, Item]:
    '''Grabs items from constants.py'''
    return {name.upper(): Item(name, idx, price) for idx, (name, price) in enumerate(ITEM_DATA)}

def get_moves() -> dict[str, Move]:
    '''Grabs moves from constants.py'''
    return {name.upper(): Move(name, Type(type), pp, power, accuracy, idx) for idx, (name, type, power, accuracy, pp) in enumerate(MOVE_DATA)}

def get_move(move_name: str):
    '''Grabs specific move from constants.py, ignoring case'''
    all_moves = get_moves()
    return all_moves[move_name.upper()]

def get_all_species() -> dict[str, Species]:
    '''Grabs species from constants.py'''
    species = {}
    for idx, (name, types, curve, stats, exp) in enumerate(POKE_DATA):
        type1, type2 = Type.Null, Type.Null
        if len(types) == 1:
            type1 = Type(types[0])
        if len(types) == 2:
            type1 = Type(types[0])
            type2 = Type(types[1])

        hp, att, defense, spd, spc = stats
        species[name.upper()] = Species(name, curve, type1, type2, hp, att, defense, spd, spc, exp, idx)
    return species

def get_species(idx) -> Species:
    '''Grabs specific species from constants.py, with either dex # or name'''
    all_species = get_all_species()
    if isinstance(idx, int):
        return next((x for x in all_species.values() if x.idx == idx), None)
    elif isinstance(idx, str):
        return all_species[idx.upper()]

def get_learnset(game: str='rb') -> list[LevelMove]:
    '''Grabs game learnset from constants.py'''
    return get_learnsets[game]

def get_learnsets() -> dict[str, list[list[LevelMove]]]:
    '''Grabs both games' learnsets from constants.py'''
    moves = list(get_moves().values())
    rb_learnsets = _parse_learnset_data(RB_LEARNSET, moves)
    y_learnsets = _parse_learnset_data(Y_LEARNSET, moves)

    return {'rb': rb_learnsets,
            'y': y_learnsets}

def _parse_learnset_data(learnset: list, moves: dict) -> list[LevelMove]:
    '''Internal parsing of learnset data'''
    # start with empty list so index = dex num
    ret = [[]]
    for l in learnset:
        ls = []
        for level, move in l:
            m = moves[move]
            ls.append(LevelMove(level, m))
        ret.append(ls)

    return ret

def get_game_trainers(game: str='rb') -> dict[int, Trainer]:
    '''Grabs game trainer data from constants.py'''
    return get_trainers()[game]

def get_trainers() -> dict[str, dict[int, Trainer]]:
    '''Grabs trainer data from constants.py'''
    species = get_all_species()
    trainer_classes = get_trainer_classes()
    learnsets = get_learnsets()

    y_trainers = _parse_trainer_data(Y_TRAINERS, trainer_classes, species, learnsets['y'])
    rb_trainers = _parse_trainer_data(RB_TRAINERS, trainer_classes, species, learnsets['rb'])

    trainers = {
        'y': y_trainers,
        'rb': rb_trainers
    }

    update_special_trainers(trainers, get_moves())

    return trainers

def _parse_trainer_data(trainer_data: dict,
                        trainer_classes: dict,
                        species: dict,
                        learnset: list
    ) -> dict[int, Trainer]:
    '''Internal parsing of trainer data'''

    ret = {}
    for trainer_class, t_data in trainer_data.items():
        for offset, poke_list in t_data.items():
            p_list = []
            for level, poke_name in poke_list:
                s = species[poke_name]
                l = learnset[s.dex_num]
                moveset = get_default_moveset(l, level)
                p_list.append(pokemon.Pokemon(s, level, game='y', moveset=moveset))
            t_class = trainer_classes[trainer_class]
            ret[offset] = Trainer(t_class, p_list, offset)
    return ret

def get_trainer_aliases() -> Tuple[dict[str, int], dict[str,int]]:
    '''Specify user-supplied trainer aliases for ease of reference

    Commented out common routed trainers that don't have an obvious alias
    '''

    y_aliases = {}
    rb_aliases = {}

    rb_aliases['WEEDLE GUY'] = 0x39dd7

    rb_aliases['BROCK'] = 0x3a3b5
    rb_aliases['BC1'] = 0x39dda
    rb_aliases['SHORTS GUY'] = 0x39d99
    rb_aliases['BC2'] = 0x39ddf
    rb_aliases['BC3'] = 0x39de5

    rb_aliases['MOON ROCKET'] = 0x3a29c
    rb_aliases['NERD'] = 0x39f2a

    rb_aliases['BRIDGE RIVAL'] = 0x3a209
    rb_aliases['BRIDGE 1'] = 0x39df2
    rb_aliases['BRIDGE 2'] = 0x39e27
    rb_aliases['BRIDGE 3'] = 0x39da5
    rb_aliases['BRIDGE 4'] = 0x39e23
    rb_aliases['BRIDGE 5'] = 0x39e80
    rb_aliases['BRIDGE ROCKET'] = 0x3a2b0

    rb_aliases['ONIX HIKER'] = 0x39f6d
    # lass 0x39E2B
    rb_aliases['BOTTOM HIKER'] = 0x39f67
    # lass 0x39E2F

    rb_aliases['DIG ROCKET'] = 0x3a2ac
    rb_aliases['GOLDEEN'] = 0x39e9d
    rb_aliases['MISTY'] = 0x3a3bb

    # jr trainer f 0x39EA4
    # jr trainer m 0x39E86
    rb_aliases['BOAT RIVAL'] = 0x3a40b
    rb_aliases['GENTLEMAN'] = 0x3a3fd
    rb_aliases['SURGE'] = 0x3a3c1

    rb_aliases['4 TURN THRASH'] = 0x39eac
    rb_aliases['VENONAT'] = 0x39e07
    rb_aliases['TUNNEL 1'] = 0x39f22
    rb_aliases['TUNNEL 2'] = 0x39f1a
    rb_aliases['ODDISH GIRL'] = 0x39ec2
    rb_aliases['TUNNEL HIKER'] = 0x39f81
    # jr trainer f 0x39EE8
    rb_aliases['GAMBLER'] = 0x3a0cd

    rb_aliases['TOWER RIVAL'] = 0x3a42b
    rb_aliases['CHANNELER 1'] = 0x3a4e3
    rb_aliases['CHANNELER 2'] = 0x3a507
    rb_aliases['CHANNELER 3'] = 0x3a504
    rb_aliases['HAUNTER'] = 0x3a4f0

    rb_aliases['TOWER ROCKET 1'] = 0x3a2ed
    rb_aliases['TOWER ROCKET 2'] = 0x3a2f2
    rb_aliases['TOWER ROCKET 3'] = 0x3a2f6

    rb_aliases['ARBOK'] = 0x3a319
    rb_aliases['SILPH RIVAL'] = 0x3a44f
    rb_aliases['SILPH ROCKET'] = 0x3a355
    rb_aliases['SILPH GIO'] = 0x3a286

    rb_aliases['JUGGLER 1'] = 0x3a13a
    rb_aliases['JUGGLER 2'] = 0x3a140

    rb_aliases['KOGA'] = 0x3a3d2 # hack without weezing exp

    rb_aliases['EGGS'] = 0x3a0db
    rb_aliases['ERIKA'] = 0x3a3c9
    rb_aliases['BLAINE'] = 0x3a3db
    rb_aliases['SABRINA'] = 0x3a3e5
    rb_aliases['RHYHORN'] = 0x3a382
    rb_aliases['BLACK BELT'] = 0x3a1da
    rb_aliases['GIO 2'] = 0x3a290

    rb_aliases['VIRIDIAN RIVAL'] = 0x3a475
    rb_aliases['LORELEI'] = 0x3a4bb
    rb_aliases['BRUNO'] = 0x3a3a9
    rb_aliases['AGATHA'] = 0x3a516
    rb_aliases['LANCE'] = 0x3a522
    rb_aliases['CHAMP'] = 0x3a49f

    y_aliases['FOREST BC1'] = 0x39e67
    y_aliases['FOREST BC2'] = 0x39e6b # metapod caterpie metapod
    y_aliases['FOREST BC3'] = 0x39e70

    y_aliases['LIGHTYEAR GUY'] = 0x39f17
    y_aliases['BROCK'] = 0x3a454

    y_aliases['RT3 BC1'] = 0x39e73
    y_aliases['SHORTS GUY'] = 0x39e2f
    y_aliases['RT3 BC2'] = 0x39e78
    y_aliases['RT3 BC3'] = 0x39e7e

    y_aliases['NERD'] = 0x39fcf
    y_aliases['MOON J&J'] = 0x3a3d9

    y_aliases['BRIDGE RIVAL'] = 0x3a292
    y_aliases['BRIDGE 1'] = 0x39e8b
    y_aliases['BRIDGE 2'] = 0x39ec4
    y_aliases['BRIDGE 3'] = 0x39e3b
    y_aliases['BRIDGE 4'] = 0x39ec0
    y_aliases['BRIDGE 5'] = 0xe9f1f
    y_aliases['BRIDGE ROCKET'] = 0x3a32f

    y_aliases['TOP HIKER'] = 0x3a008
    y_aliases['BOTTOM HIKER'] = 0x3a012
    # lass
    # top guy
    # lass

    y_aliases['GOLDEEN'] = 0x39f3f
    y_aliases['MISTY'] = 0x3a45a

    y_aliases['DIG ROCKET'] = 0x3a32b
    # jr f
    # jr m
    y_aliases['BOAT RIVAL'] = 0x3a499
    y_aliases['GENTLEMAN'] = 0x3a495
    y_aliases['SURGE'] = 0x3a460

    y_aliases['4 TURN THRASH'] = 0x39f4e
    y_aliases['VENONAT'] = 0x39ea0
    y_aliases['TUNNEL 1'] = 0x39fc7
    y_aliases['TUNNEL 2'] = 0x39fbf
    y_aliases['ODDISH GIRL'] = 0x39f64
    y_aliases['TUNNEL HIKER'] = 0x3a026
    # jr f
    y_aliases['GAMBLER'] = 0x3a172
    y_aliases['CLEF LASS'] = 0x39ee8

    y_aliases['VAPE TOWER RIVAL'] = 0x3a4bb
    y_aliases['TOWER RIVAL'] = 0x3a4af
    y_aliases['CHANNELER 1'] = 0x3a551
    y_aliases['CHANNELER 2'] = 0x3a558
    y_aliases['CHANNELER 3'] = 0x3a558
    y_aliases['TOWER J&J'] = 0x3a3e3

    y_aliases['MACHOKE ROCKET'] = 0x3a3ca
    y_aliases['ARBOK'] = 0x3a398
    y_aliases['VAPE SILPH RIVAL'] = 0x3a4df
    y_aliases['SILPH RIVAL'] = 0x3a4d3
    y_aliases['SILPH J&J'] = 0x3a3e8
    y_aliases['SILPH GIO'] = 0x3a305
    y_aliases['SABRINA'] = 0x3a47e

    y_aliases['JUGGLER 1'] = 0x3a1df
    y_aliases['JUGGLER 2'] = 0x3a1e5
    y_aliases['KOGA'] = 0x3a46c
    y_aliases['BLAINE'] = 0x3a476
    y_aliases['EGGS'] = 0x3a180
    y_aliases['ERIKA'] = 0x3a464

    y_aliases['RHYHORN'] = 0x3a421
    y_aliases['BLACK BELT'] = 0x3a27f
    y_aliases['GIO 2'] = 0x3a30f

    y_aliases['VAPE VIRIDIAN RIVAL'] = 0x3a507
    y_aliases['VIRIDIAN RIVAL'] = 0x3a4f9
    y_aliases['LORELEI'] = 0x3a53f
    y_aliases['BRUNO'] = 0x3a448
    y_aliases['AGATHA'] = 0x3a59a
    y_aliases['LANCE'] = 0x3a5a6
    y_aliases['VAPE CHAMP'] = 0x3a531
    y_aliases['CHAMP'] = 0x3a523

    return {'y': y_aliases, 'rb': rb_aliases}

def update_special_trainers(trainers: dict, moves: dict) -> None:
    '''Update trainers with different movesets

    Mostly gym leaders/rival fights, but some other random trainers have
    different movesets as well.
    '''

    y_trainers = trainers['y']
    y_trainers[0x39EA5].set_move(2, 2, moves["TACKLE"])
    y_trainers[0x39EA5].set_move(2, 3, moves["STRING SHOT"])

    # YOUNGSTER, 14
    y_trainers[0x39E64].set_move(1, 4, moves["FISSURE"])

    # BROCK, 1
    y_trainers[0x3A454].set_move(2, 3, moves["BIND"])
    y_trainers[0x3A454].set_move(2, 4, moves["BIDE"])

    # MISTY, 1
    y_trainers[0x3A45A].set_move(2, 4, moves["BUBBLEBEAM"])

    # LT_SURGE, 1
    y_trainers[0x3A460].set_move(1, 1, moves["THUNDERBOLT"])
    y_trainers[0x3A460].set_move(1, 2, moves["MEGA PUNCH"])
    y_trainers[0x3A460].set_move(1, 3, moves["MEGA KICK"])
    y_trainers[0x3A460].set_move(1, 4, moves["GROWL"])

    # ERIKA, 1
    y_trainers[0x3A464].set_move(1, 3, moves["MEGA DRAIN"])
    y_trainers[0x3A464].set_move(2, 1, moves["RAZOR LEAF"])
    y_trainers[0x3A464].set_move(3, 1, moves["PETAL DANCE"])

    # KOGA, 1
    y_trainers[0x3A46C].set_move(1, 1, moves["TOXIC"])
    y_trainers[0x3A46C].set_move(1, 2, moves["TACKLE"])
    y_trainers[0x3A46C].set_move(2, 1, moves["TOXIC"])
    y_trainers[0x3A46C].set_move(2, 3, moves["SUPERSONIC"])
    y_trainers[0x3A46C].set_move(3, 1, moves["TOXIC"])
    y_trainers[0x3A46C].set_move(3, 2, moves["DOUBLE-EDGE"])
    y_trainers[0x3A46C].set_move(4, 1, moves["LEECH LIFE"])
    y_trainers[0x3A46C].set_move(4, 2, moves["DOUBLE TEAM"])
    y_trainers[0x3A46C].set_move(4, 3, moves["PSYCHIC"])
    y_trainers[0x3A46C].set_move(4, 4, moves["TOXIC"])

    # BLAINE, 1
    y_trainers[0x3A476].set_move(1, 1, moves["FLAMETHROWER"])
    y_trainers[0x3A476].set_move(1, 4, moves["CONFUSE RAY"])
    y_trainers[0x3A476].set_move(3, 1, moves["FLAMETHROWER"])
    y_trainers[0x3A476].set_move(3, 2, moves["FIRE BLAST"])
    y_trainers[0x3A476].set_move(3, 3, moves["REFLECT"])

    # SABRINA, 1
    y_trainers[0x3A47E].set_move(1, 1, moves["FLASH"])
    y_trainers[0x3A47E].set_move(2, 1, moves["KINESIS"])
    y_trainers[0x3A47E].set_move(2, 4, moves["PSYWAVE"])
    y_trainers[0x3A47E].set_move(3, 1, moves["PSYWAVE"])

    # GIOVANNI, 3
    y_trainers[0x3A30F].set_move(1, 3, moves["FISSURE"])
    y_trainers[0x3A30F].set_move(2, 2, moves["DOUBLE TEAM"])
    y_trainers[0x3A30F].set_move(3, 1, moves["EARTHQUAKE"])
    y_trainers[0x3A30F].set_move(3, 3, moves["THUNDER"])
    y_trainers[0x3A30F].set_move(4, 1, moves["EARTHQUAKE"])
    y_trainers[0x3A30F].set_move(4, 2, moves["LEER"])
    y_trainers[0x3A30F].set_move(4, 3, moves["THUNDER"])
    y_trainers[0x3A30F].set_move(5, 1, moves["ROCK SLIDE"])
    y_trainers[0x3A30F].set_move(5, 4, moves["EARTHQUAKE"])

    # LORELEI, 1
    y_trainers[0x3A53F].set_move(1, 1, moves["BUBBLEBEAM"])
    y_trainers[0x3A53F].set_move(2, 3, moves["ICE BEAM"])
    y_trainers[0x3A53F].set_move(3, 1, moves["PSYCHIC"])
    y_trainers[0x3A53F].set_move(3, 2, moves["SURF"])
    y_trainers[0x3A53F].set_move(4, 3, moves["LOVELY KISS"])
    y_trainers[0x3A53F].set_move(5, 3, moves["BLIZZARD"])

    # BRUNO, 1
    y_trainers[0x3A448].set_move(1, 1, moves["ROCK SLIDE"])
    y_trainers[0x3A448].set_move(1, 2, moves["SCREECH"])
    y_trainers[0x3A448].set_move(1, 4, moves["DIG"])
    y_trainers[0x3A448].set_move(2, 3, moves["FIRE PUNCH"])
    y_trainers[0x3A448].set_move(2, 4, moves["DOUBLE TEAM"])
    y_trainers[0x3A448].set_move(3, 1, moves["DOUBLE KICK"])
    y_trainers[0x3A448].set_move(3, 2, moves["MEGA KICK"])
    y_trainers[0x3A448].set_move(3, 4, moves["DOUBLE TEAM"])
    y_trainers[0x3A448].set_move(4, 1, moves["ROCK SLIDE"])
    y_trainers[0x3A448].set_move(4, 2, moves["SCREECH"])
    y_trainers[0x3A448].set_move(4, 4, moves["EARTHQUAKE"])
    y_trainers[0x3A448].set_move(5, 2, moves["KARATE CHOP"])
    y_trainers[0x3A448].set_move(5, 3, moves["STRENGTH"])

    # AGATHA, 1
    y_trainers[0x3A59A].set_move(1, 2, moves["SUBSTITUTE"])
    y_trainers[0x3A59A].set_move(1, 3, moves["LICK"])
    y_trainers[0x3A59A].set_move(1, 4, moves["MEGA DRAIN"])
    y_trainers[0x3A59A].set_move(2, 2, moves["TOXIC"])
    y_trainers[0x3A59A].set_move(2, 4, moves["LEECH LIFE"])
    y_trainers[0x3A59A].set_move(3, 2, moves["LICK"])
    y_trainers[0x3A59A].set_move(4, 1, moves["WRAP"])
    y_trainers[0x3A59A].set_move(5, 2, moves["PSYCHIC"])

    # LANCE, 1
    y_trainers[0x3A5A6].set_move(1, 1, moves["DRAGON RAGE"])
    y_trainers[0x3A5A6].set_move(2, 1, moves["THUNDER WAVE"])
    y_trainers[0x3A5A6].set_move(2, 3, moves["THUNDERBOLT"])
    y_trainers[0x3A5A6].set_move(3, 1, moves["BUBBLEBEAM"])
    y_trainers[0x3A5A6].set_move(3, 2, moves["WRAP"])
    y_trainers[0x3A5A6].set_move(3, 3, moves["ICE BEAM"])
    y_trainers[0x3A5A6].set_move(4, 1, moves["WING ATTACK"])
    y_trainers[0x3A5A6].set_move(4, 2, moves["SWIFT"])
    y_trainers[0x3A5A6].set_move(4, 3, moves["FLY"])
    y_trainers[0x3A5A6].set_move(5, 1, moves["BLIZZARD"])
    y_trainers[0x3A5A6].set_move(5, 2, moves["FIRE BLAST"])
    y_trainers[0x3A5A6].set_move(5, 3, moves["THUNDER"])

    # RIVAL3, 1 (JOLTEON)
    y_trainers[0x3A515].set_move(1, 3, moves["EARTHQUAKE"])
    y_trainers[0x3A515].set_move(2, 4, moves["KINESIS"])
    y_trainers[0x3A515].set_move(3, 4, moves["LEECH SEED"])
    y_trainers[0x3A515].set_move(4, 1, moves["ICE BEAM"])
    y_trainers[0x3A515].set_move(5, 1, moves["CONFUSE RAY"])
    y_trainers[0x3A515].set_move(5, 4, moves["FIRE SPIN"])
    y_trainers[0x3A515].set_move(6, 3, moves["QUICK ATTACK"])

    # RIVAL3, 2 (FLAREON)
    y_trainers[0x3A523].set_move(1, 3, moves["EARTHQUAKE"])
    y_trainers[0x3A523].set_move(2, 4, moves["KINESIS"])
    y_trainers[0x3A523].set_move(3, 4, moves["LEECH SEED"])
    y_trainers[0x3A523].set_move(4, 1, moves["THUNDERBOLT"])
    y_trainers[0x3A523].set_move(5, 1, moves["ICE BEAM"])
    y_trainers[0x3A523].set_move(6, 2, moves["REFLECT"])
    y_trainers[0x3A523].set_move(6, 3, moves["QUICK ATTACK"])

    # RIVAL3, 3 (VAPOREON)
    y_trainers[0x3A531].set_move(1, 3, moves["EARTHQUAKE"])
    y_trainers[0x3A531].set_move(2, 4, moves["KINESIS"])
    y_trainers[0x3A531].set_move(3, 4, moves["LEECH SEED"])
    y_trainers[0x3A531].set_move(4, 1, moves["CONFUSE RAY"])
    y_trainers[0x3A531].set_move(4, 4, moves["FIRE SPIN"])
    y_trainers[0x3A531].set_move(5, 1, moves["THUNDERBOLT"])
    y_trainers[0x3A531].set_move(6, 1, moves["AURORA BEAM"])
    y_trainers[0x3A531].set_move(6, 3, moves["QUICK ATTACK"])

    rb_trainers = trainers['rb']
    rb_trainers[0x3A3B5].set_move(1, 2, moves["BIDE"], False)
    rb_trainers[0x3A3BB].set_move(1, 2, moves["BUBBLEBEAM"], False)
    rb_trainers[0x3A3C1].set_move(2, 2, moves["THUNDERBOLT"], False)
    rb_trainers[0x3A3C9].set_move(2, 2, moves["MEGA DRAIN"], False)
    rb_trainers[0x3A3D1].set_move(3, 2, moves["TOXIC"], False)
    rb_trainers[0x3A3E5].set_move(3, 2, moves["PSYWAVE"], False)
    rb_trainers[0x3A3DB].set_move(3, 2, moves["FIRE BLAST"], False)
    rb_trainers[0x3A290].set_move(4, 2, moves["FISSURE"], False)

    # teammoves (e4)
    # in theory this is a different system, in practice we can use the same one
    rb_trainers[0x3A4BB].set_move(4, 2, moves["BLIZZARD"], False)
    rb_trainers[0x3A3A9].set_move(4, 2, moves["FISSURE"], False)
    rb_trainers[0x3A516].set_move(4, 2, moves["TOXIC"], False)
    rb_trainers[0x3A522].set_move(4, 2, moves["BARRIER"], False)

    # champion rival
    # two moves per roster: pidgeot sky attack, starter elemental move
    # ref https:#github.com/pret/pokered/blob/47cd734276eade428671f720e8d01a45c4fd2bc2/engine/battle/read_trainer_party.asm#L126
    rb_trainers[0x3A491].set_move(0, 2, moves["SKY ATTACK"], False)
    rb_trainers[0x3A49F].set_move(0, 2, moves["SKY ATTACK"], False)
    rb_trainers[0x3A4AD].set_move(0, 2, moves["SKY ATTACK"], False)

    rb_trainers[0x3A491].set_move(5, 2, moves["BLIZZARD"], False)
    rb_trainers[0x3A49F].set_move(5, 2, moves["MEGA DRAIN"], False)
    rb_trainers[0x3A4AD].set_move(5, 2, moves["FIRE BLAST"], False)

def get_learnset(dex_number, game='rb'):
    learnsets = get_learnsets()
    return learnsets[game][dex_number]

if __name__ == '__main__':
    pass
