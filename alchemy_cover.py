from absl import app
from absl import flags
import attr
import bidict
import csv
import collections
import itertools
import random
from typing import (
    AbstractSet,
    Set,
    List,
    FrozenSet,
    Dict,
    Text,
    Mapping,
    Iterable,
    Generator,
    NewType,
    Tuple,
)

FLAGS = flags.FLAGS

flags.DEFINE_string("infile", None, "CSV to read ingredient data from")
flags.DEFINE_string("outfile", None, "CSV to write potions to")


IngredientId = NewType("IngredientId", int)
EffectId = NewType("EffectId", int)
IngredientEffect = Tuple[IngredientId, EffectId]


EFFECT_INDEX = None
INGREDIENT_INDEX = None


def _repr_ingredient_id(value: IngredientId) -> Text:
    return repr(INGREDIENT_INDEX[value])


def _repr_ingredients(value: Iterable[IngredientId]) -> Text:
    return "[" + ", ".join(_repr_ingredient_id(i) for i in value) + "]"


def _repr_effect_id(value: EffectId) -> Text:
    return repr(EFFECT_INDEX[value])


def _repr_effects(value: Iterable[EffectId]) -> Text:
    return "[" + ", ".join(_repr_effect_id(e) for e in value) + "]"


def _repr_ing_effect(value: IngredientEffect) -> Text:
    return "({}, {})".format(_repr_ingredient_id(value[0]), _repr_effect_id(value[1]),)


def _repr_ing_effects(value: Iterable[IngredientEffect]) -> Text:
    return "[" + ", ".join(_repr_ing_effect(e) for e in value) + "]"


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return itertools.islice(iterable, n)


@attr.s(frozen=True)
class Ingredient(object):
    name: IngredientId = attr.ib(repr=_repr_ingredient_id)
    effects: FrozenSet[EffectId] = attr.ib(repr=_repr_effects, converter=frozenset)

    @property
    def display_name(self) -> Text:
        return INGREDIENT_INDEX.inverse[self.name]


@attr.s(frozen=True)
class Potion(object):
    ingredients: FrozenSet[IngredientId] = attr.ib(
        repr=_repr_ingredients, converter=frozenset
    )
    ingredient_effects: FrozenSet[IngredientEffect] = attr.ib(
        repr=_repr_ing_effects, converter=frozenset
    )

    @property
    def effects(self) -> FrozenSet[EffectId]:
        return frozenset(e[1] for e in self.ingredient_effects)


def greedy_set_cover(universe: Iterable[IngredientEffect], potions: Iterable[Potion]):
    chosen: Set[Potion] = set()
    left: Set[IngredientEffect] = set(universe)
    unchosen: Set[Potion] = set(potions)

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

        # print(len(left), len(next_covered), next_set)

        unchosen.remove(next_set)
        chosen.add(next_set)
        left -= next_set.ingredient_effects

    return chosen


def read_problem(fname) -> Dict[Text, FrozenSet[Text]]:
    ingredients = {}
    with open(fname, "r") as f:
        for row in csv.DictReader(f, delimiter=","):
            ingredients[row["Ingredient"]] = frozenset(
                [row["Effect1"], row["Effect2"], row["Effect3"], row["Effect4"]]
            )
    return ingredients


def numberize(
    ingredients: Mapping[Text, FrozenSet[Text]],
) -> Generator[Ingredient, None, None]:
    numbered = {}
    for ingredient, effects in ingredients.items():
        yield Ingredient(
            name=INGREDIENT_INDEX.inverse[ingredient],
            effects=frozenset(EFFECT_INDEX.inverse[eff] for eff in effects),
        )


def potions(ingredients: Iterable[Ingredient]) -> Generator[Potion, None, None]:
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


def _write_potions(fname, resulting_potions):
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
        for pot in resulting_potions:
            ing_names = [INGREDIENT_INDEX[ing] for ing in pot.ingredients]
            eff_names = [EFFECT_INDEX[eff] for eff in pot.effects]
            writer.writerow(ing_names + eff_names)


def main(args):
    del args  # unused

    global EFFECT_INDEX
    global INGREDIENT_INDEX

    ingredients = read_problem(FLAGS.infile)
    print("Read {} ingredients".format(len(ingredients)))

    # Populate mappings
    all_effects = frozenset(itertools.chain.from_iterable(ingredients.values()))
    EFFECT_INDEX = bidict.frozenbidict(enumerate(all_effects))
    INGREDIENT_INDEX = bidict.frozenbidict(enumerate(ingredients.keys()))

    ingredients = list(numberize(ingredients))
    print("Ingredients numberized")

    all_potions = set(potions(ingredients))
    print("Constructed {} potions".format(len(all_potions)))

    all_ingredient_effects = frozenset(
        itertools.chain.from_iterable(p.ingredient_effects for p in all_potions)
    )
    print("Need to find {} ingredient-effect pairs".format(len(all_ingredient_effects)))

    result = greedy_set_cover(all_ingredient_effects, all_potions)
    print("Found a solution using {} potions, writing to csv...".format(len(result)))

    _write_potions(FLAGS.outfile, result)


if __name__ == "__main__":
    flags.mark_flag_as_required("infile")
    flags.mark_flag_as_required("outfile")
    app.run(main)
