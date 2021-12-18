<p align="center">
  <img src="logo.svg" height="100px"/>
</p>

This repository acts as an online database of Pokémon related game data, primarily for use in pkuManager. Data is grouped together in a JSON file called a **datadex**. There are different types of datadexes like species dexes, ability dexes, move dexes, etc. A list of all dexes of a particular type are in the [dexlist.json](scripts/Compile%20Masterdexes/dexlist.json). Before each commit, these lists are compiled into a **master datadex** of that type. These masterdexes are then used by applications like [pkuManager](https://github.com/project-pku/pkuManager).