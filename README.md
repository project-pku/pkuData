<p align="center">
  <img src="logo.svg" height="100px"/>
</p>

This repository acts as an online database of Pokémon related game data, primarily for use in pkuManager. Data is grouped together in a JSON file called a **datadex**. There are different types of datadexes like species dexes, ability dexes, move dexes, etc. For each of these types, there exists a **master datadex** containing a list of all datadexes of that type. Internally, pkuManager combines them all into a single datadex to be used in its logic.