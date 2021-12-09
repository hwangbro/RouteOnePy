# YAML Route Files

There are two main sections you need for a valid route file: a `config` section and a `route` section

## config

This section specifies the metadata for the route file.

#### game

Represents what game you are routing for. Inputs must be either `rb` or `y`

#### species

Represents what pokemon you are using. The species name should contain no spaces. You can look in [POKE_DATA](constants.py#L56) to check names if you're not sure

#### level

Starting level

#### ivs

IVs (DVs) of the pokemon you're using

#### default_verbosity

(OPTIONAL). Sets a default verbosity level to be used when verbosity is not explicitly set. Setting verbosity to `0` means no output will be give, `1` means that limited information about the fight is outputted, and `2` is full fight data, including damage range rolls.

#### starting_money

(OPTIONAL). Sets the starting money

#### output

Specifies the path to the output file that will be created.

## route

This section is where you specify the route details. Every item in this section should start with a hyphen, as seen in some of the examples.

#### fight

Specifies a trainer to fight.

- `id`: Expects either the hex offset or a string alias. Existing aliases can be found in [data.py](data.py#L120), otherwise the hex offsets can be found using [pokeworld](https://www.extratricky.com/pokeworld/rb/1) or [constants.py](constants.py#L925)
    - You can specify multiple trainers to fight in the same action, and stat modifiers will be applied to all. However, you cannot use variations/range_checks
- `split` (OPTIONAL): Determines how many ways to split the exp and stat exp. Defaults to 1, meaning the exp is not split at all.
- `verbose` (OPTIONAL): Determines the verbosity of this particular action. If not supplied, defaults to the `default_verbosity` if set, otherwise defaults to `0`, meaning no output is supplied
- `att_mod`: Determines the attacker's stat modifiers. There are two sections to a stat modifier, and one or both can be supplied.
    - `stages`: Refers to stat stages affected by moves like `Tail Whip` or `Growl`. Expects in the form `#/#/#/#` representing `att/def/speed/special`
        - e.g. `0/-1/0/0` would mean that the attacker has -1 defense
    - `bbs`: Refers to badge boosts. These are reapplied badge boosts; the original badge boost will be applied automatically if you've beaten the corresponding gym trainer or specifying `get badge`
        - e.g. `1/0/0/0` would mean that the attacker has +1 attack badge boosts
- `def_mod`: Determines the defender's stat modifiers. Same format as `att_mod`
- `variations`: You can specify different fight variations using this structure. This is useful if you want to see how damage ranges can change with different stat modifiers without having to re-run the tool every time.
    - First, you need to specify what pokemon this variation is for. This is done by either using the pokemon order #, or using `all` if the variation is for the whole fight
    - On the next level, you can specify any number of variations you want. Each of them should have their own name.
    - Each variation can accept `att_mod` and `def_mod` structures, outlined above.
- ```
    variations:
        1: # <--- specifies what pokemon this fight variation is targetting.
            1 bb: # <--- variation name, can be anything
                att_mod:
                    bbs: 1/0/0/0
            2 bb:
                att_mod:
                    bbs: 2/0/0/0
            2 bb -1 defense:
                att_mod:
                    bbs: 2/0/0/0
                def_mod:
                    stages: 0/-1/0/0
        2: # <--- specifies what pokemon, in this case, the 2nd
            +1:
                att_mod:
                    stages: 1/0/0/0
        all: # <--- specifies variation for the entire fight
            -1 def:
                att_mod:
                    stages: 0/-1/0/0
- `range_check`: Used to check the kill chance for any number of turns and any combination of moves and stat modifiers.
    - First, you need to specify what pokemon this range check is for.
    - On the next level, you can specify any number of range checks you want. Each of them should have their own name.
    - Each variation must provide `turns`, `moves`.
    - `turns` is how many turns the variation is for
    - `moves` can either be one move used for every turn, or a comma separated list of moves
        - e.g. `Horn Attack`, or `Horn Attack, Tackle`
    - `att_mod` and `def_mod` can both be specified.
        - For `stages` and `bbs`, you can specify a comma separated list to specify each turn.
        - e.g. `stages: 0/0/0/0, 1/0/0/0` would represent having +1 attack for the second turn only
        - If only one value is provided, it assumes that this value is used for all turns
- ```
    range_check:
        1: # <--- specifies what pokemon this range check is targetting
            1 bb: # <--- range_check name, can be anything
                turns: 2
                moves: Horn Attack
                att_mod:
                    bbs: 0/0/0/0, 1/0/0/0
                def_mod:
                    stages: 0/-1/0/0 # applies to both turns
            3 ha:
                turns: 3
                moves: Horn Attack
            ha tackle:
                turns: 2
                moves: Horn Attack, Tackle

### I would highly recommend checking [red.yaml](example_routes/red.yaml) as an example.

#### wild

Similar format to the fight action, but used for wild encounters.

- `id`: Expects a string in the form of `L<#> <SPECIES>`. e.g. `L3 PIDGEY` or `L2 RATTATA`
    - like fight, you can specify multiple wild pokemon in the same action and stat modifiers will be applied to all, but you cannot use variations/range_checks if doing so
- `wild_ivs` (OPTIONAL): Expects a hex integer representing the DVs. Defaults to 0x9888
- `variations`: same as fight, but you can also specify different wild_ivs as well
- `range_checks`: same as fight
- `att_mod`: same as fight
- `def_mod`: same as fight

Examples

Fight with variation
```
    - wild:
        id: L3 PIDGEY
        wild_ivs: 0x0000
        variations:
            all:
                god_pidgey:
                    wild_ivs: 0xffff
```

Multiple Pokemon
```
    - wild:
        id:
            - L3 PIDGEY
            - L2 RATTATA
        wild_ivs: 0x0000
        def_mod:
            stages: 0/-1/0/0
```

#### learn move

Adds the specified move to the current moveset. You are not limited to only 4 moves for flexibility of routing.

e.g. `learn move: THUNDERBOLT`

#### unlearn move

Removes the specified move from the current moveset. Will not throw an error if the move is not there.

e.g. `unlearn move: POISON STING`

#### use item

Uses a vitamin or a rare candy.

e.g. `use item: RARE CANDY` or `use item: PROTEIN`

#### print stats

Prints out the current possible stat values given the full range of possible DVs

#### get badge

Badge boosts are automatically obtained after beating the subsequent gym leaders. If they are not beaten in this route file (e.g. alt main is caught after you beat brock), you can specify the badge with this action.

You can either specify the full badge name (`boulderbadge`, `soulbadge`, `thunderbadge`, `volcanobadge`), or simplify to the stat (`att`, `def`, `spd`, `spc`/`spec`)

For example, `get badge: att` is the same as `get badge: boulderbadge`

#### evolve

Evolves the current pokemon to the one specified in this option. This program does _not_ know what evolutions are automatically, so one must be provided

#### print money

Prints the current money total
