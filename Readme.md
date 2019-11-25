# Alchemy Solvers for Skyrim

![](https://github.com/vebyast/skyrim_alchemy/workflows/CI/badge.svg)

I've provided the two datasets that I've worked with so far:

- `data/skyrim_vanilla.csv` is the vanilla set of potion ingredients
  from TES5 + DCLs [as listed on Skyrim
  Wiki](https://elderscrolls.fandom.com/wiki/Ingredients_(Skyrim)). There's
  a... small chance that there are some errors in it. I haven't dug in
  particularly deeply.
- `data/skyrim_lexy_legacy_of_the_dragonborn.csv` is the set of
  ingredients in [Lexy's Legacy of the
  Dragonborn](https://wiki.nexusmods.com/index.php/User:Darkladylexy/Lexys_LOTD_SE)
  modlist that are involved in TES5, DLCs, and the Complete Alchemy
  and Cooking Overhaul, minus the "distilled" ingredients you get from
  the level 90 perk in CACO and ingredients from some other
  mods. Thanks to
  [/u/grammarcommander](https://www.reddit.com/user/grammarcommander)
  on reddit for dumping the data for me.

To use this on your own modded game, you can extract the alchemy data
from the mod files. The alchemy data is found in the `.esp` files,
which you can inspect with the Creation Kit. If the mod comes packaged
as a `.bsa`, you may need to install the mod or use a program like BAE
to get at the `.esp` files.

## Tools

### alchemy_cover.py

Figure out what potions to brew to discover all ingredient effects.

## Installation and Development

Dependency management and setup are managed by `pipenv`. Linting is
done with `pylint` and `pytype`. The project is fully
type-hinted. Formatting is handled with `black` and `isort`. PRs must
lint.

To get started:

```bash
git clone https://github.com/vebyast/skyrim_alchemy.git
cd skyrim_alchemy
pipenv install --dev
pipenv run python alchemy/alchemy_cover.py \
    --infile=data/skyrim_vanilla.csv \
	--outfile=output/skyrim_vanilla_1.csv
```
