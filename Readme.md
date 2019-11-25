# Alchemy Solvers for Skyrim

![](https://github.com/vebyast/skyrim_alchemy/workflows/CI/badge.svg)

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

## alchemy_cover.py

Figure out what potions to brew to discover all ingredient effects.
