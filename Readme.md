# Alchemy Solvers for Skyrim

I've provided the two datasets that I've worked with so far:

- `data/skyrim_vanilla.csv` is the vanilla set of potion ingredients
  from TES5 + DCLs [as listed on Skyrim
  Wiki](https://elderscrolls.fandom.com/wiki/Ingredients_(Skyrim)).
- `data/skyrim_lexy_legacy_of_the_dragonborn.csv` is the set of
  ingredients in Lexy's Legacy of the Dragonborn modlist that are
  involved in TES5, DLCs, and the Complete Alchemy and Cooking
  Overhaul, minus the "distilled" ingredients you get from the level
  90 perk in CACO and ingredients from some other mods. Thanks to
  [/u/grammarcommander](https://www.reddit.com/user/grammarcommander)
  on reddit for dumping the data for me.

To use this on your own modded game, you can extract the alchemy data
from the mod files. The alchemy data is found in the `.esp` files,
which you can inspect with the Creation Kit. If the mod comes packaged
as a `.bsa`, you may need to install the mod or use a pgoram like BAE
to get at the `.esp` files.

## Contents

### alchemy_cover.py

Computes efficient sets of potions to brew to discover the effects of
all ingredients.

This is set cover:

> Given a set of elements { 1 , 2 , . . . , n } (called the universe)
> and a collection S of m sets whose union equals the universe, the
> set cover problem is to identify the smallest sub-collection of S
> whose union equals the universe.
>
> [Set Cover on Wikipedia](https://en.wikipedia.org/wiki/Set_cover_problem)

The universe 𝑈 is the set of all `(ingredient, effect)` tuples. Each
potion is a member 𝑠 ∈ 𝑆 that covers the set of `(ingredient, effect)`
tuples that would be discovered by brewing that potion.

`alchemy_cover.py` implements the [trivial greedy
algorithm](https://en.wikipedia.org/wiki/Set_cover_problem#Greedy_algorithm),
which turns out to be decent for this domain. Ties are broken randomly
so we can rerun the program to generate new solutions.

To run the program once, invoke:

```bash
pipenv install
pipenv run python alchemy_cover.py \
    --infile=data/skyrim_vanilla.csv \
	--outfile=output/skyrim_vanilla_1.csv
```

To run it with parallelism, install [GNU
Parallel](https://www.gnu.org/software/parallel/) and invoke:

```bash
pipenv install
pipenv run python alchemy_cover_parallel.py \
	--count=30 \
	--infile=data/skyrim_vanilla.csv \
	--outfile_base='output/skyrim_vanilla_{}.csv'
```
