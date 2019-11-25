"""Figure out what potions to brew to discover all ingredient effects.

This is the set cover problem:

> Given a set of elements { 1 , 2 , . . . , n } (called the universe)
> and a collection S of m sets whose union equals the universe, the
> set cover problem is to identify the smallest sub-collection of S
> whose union equals the universe.
>
> Set Cover on Wikipedia [1]

The universe 𝑈 is the set of all `(ingredient, effect)` tuples. Each
potion is a member 𝑠 ∈ 𝑆 that covers the set of `(ingredient, effect)`
tuples that would be discovered by brewing that potion.

`alchemy_cover.py` implements the trivial greedy algorithm [2], which
turns out to be decent for this domain. Ties are broken randomly so we
can rerun the program to generate new solutions.

To run the program once, invoke:

```bash
pipenv install
pipenv run python alchemy/alchemy_cover.py \
    --infile=data/skyrim_vanilla.csv \
	--outfile=output/skyrim_vanilla_1.csv
```

To run it with parallelism, install [GNU
Parallel](https://www.gnu.org/software/parallel/) and invoke:

```bash
pipenv install
pipenv run python alchemy/alchemy_cover_parallel.py \
	--count=30 \
	--infile=data/skyrim_vanilla.csv \
	--outfile_base='output/skyrim_vanilla_{}.csv'
```

1: https://en.wikipedia.org/wiki/Set_cover_problem
2: https://en.wikipedia.org/wiki/Set_cover_problem#Greedy_algorithm

"""

import collections
import csv
import itertools
import random
from typing import FrozenSet
from typing import Generator
from typing import Iterable
from typing import List
from typing import NewType
from typing import Set
from typing import Tuple

import attr
from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string("infile", None, "CSV to read ingredient data from")

flags.DEFINE_string("outfile", None, "CSV to write potions to")

# Use strong types to help catch errors.
IngredientId = NewType("IngredientId", str)
EffectId = NewType("EffectId", str)
IngredientEffect = Tuple[IngredientId, EffectId]


@attr.s(frozen=True)
class Ingredient(object):
    """Container object for Ingredients."""

    name: IngredientId = attr.ib()
    effects: FrozenSet[EffectId] = attr.ib(converter=frozenset)


@attr.s(frozen=True)
class Potion(object):
    """Container object for Potions."""

    ingredients: FrozenSet[IngredientId] = attr.ib(converter=frozenset)
    ingredient_effects: FrozenSet[IngredientEffect] = attr.ib(converter=frozenset)

    @property
    def effects(self) -> FrozenSet[EffectId]:
        return frozenset(e[1] for e in self.ingredient_effects)


def greedy_set_cover(universe: Iterable[IngredientEffect], pots: Iterable[Potion]):
    """Solves the set cover problem using the trivial greedy algorithm."""
    chosen: Set[Potion] = set()
    left: Set[IngredientEffect] = set(universe)
    unchosen: Set[Potion] = set(pots)

    covered = lambda s: left & s.ingredient_effects

    while left:
        if not unchosen:
            raise Exception("No set cover possible")

        # Adding a random float from [0, 1) randomly breaks ties
        # between items with the same score, giving us the ability to
        # rerun to get different solutions.
        next_set: Potion = max(
            unchosen, key=lambda s: len(covered(s)) + random.random()
        )

        next_covered = covered(next_set)
        if not next_covered:
            raise Exception("No set cover possible")

        unchosen.remove(next_set)
        chosen.add(next_set)
        left -= next_set.ingredient_effects

    return chosen


def read_problem(fname) -> List[Ingredient]:
    """Reads a CSV of ingredients and effects."""
    ingredients = []
    with open(fname, "r") as f:
        for row in csv.DictReader(f, delimiter=","):
            ingredients.append(
                Ingredient(
                    name=IngredientId(row["Ingredient"]),
                    effects=frozenset(
                        [
                            EffectId(row["Effect1"]),
                            EffectId(row["Effect2"]),
                            EffectId(row["Effect3"]),
                            EffectId(row["Effect4"]),
                        ]
                    ),
                )
            )
    return ingredients


def generate_potions(
    ingredients: Iterable[Ingredient],
) -> Generator[Potion, None, None]:
    """Generate all of the potions that you can make with a set of Ingredients."""
    all_combos = itertools.chain(
        itertools.combinations(ingredients, 3), itertools.combinations(ingredients, 2),
    )
    for combination in all_combos:
        effects_counter = collections.Counter(
            itertools.chain.from_iterable(i.effects for i in combination)
        )
        effects = frozenset(eff for eff, count in effects_counter.items() if count > 1)
        ingredient_effects: FrozenSet[IngredientEffect] = frozenset(
            (i.name, e)
            for i, e in itertools.product(combination, effects)
            if e in i.effects
        )
        if effects:
            yield Potion(
                ingredients=frozenset(i.name for i in combination),
                ingredient_effects=ingredient_effects,
            )


def write_potions(fname, resulting_potions):
    """Formats the given potions as csv and writes them out."""
    lines = []
    for pot in resulting_potions:
        ing_names = sorted(pot.ingredients)
        eff_names = sorted(pot.effects)
        line = ing_names + eff_names + [None] * (6 - len(eff_names))
        lines.append(line)
    lines.sort()
    with open(fname, "w") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Ingredient1",
                "Ingredient2",
                "Ingredient3",
                "Effect1",
                "Effect2",
                "Effect3",
                "Effect4",
                "Effect5",
                "Effect6",
            ]
        )
        for line in lines:
            writer.writerow(line)


def main(args):
    """Entry point."""
    del args  # unused

    ingredients: List[Ingredient] = read_problem(FLAGS.infile)
    print("Read {} ingredients".format(len(ingredients)))

    all_potions: Set[Potion] = set(generate_potions(ingredients))
    print("Constructed {} potions".format(len(all_potions)))

    all_ingredient_effects = frozenset(
        itertools.chain.from_iterable(p.ingredient_effects for p in all_potions)
    )
    print(
        "Finding a cover for {} ingredient-effect pairs".format(
            len(all_ingredient_effects)
        )
    )

    result = greedy_set_cover(all_ingredient_effects, all_potions)
    print("Found a solution using {} potions, writing to csv...".format(len(result)))

    write_potions(FLAGS.outfile, result)


if __name__ == "__main__":
    flags.mark_flag_as_required("infile")
    flags.mark_flag_as_required("outfile")
    app.run(main)
