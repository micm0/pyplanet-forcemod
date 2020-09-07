# pyplanet-forcemod
PyPlanet app that can force a mod url for all maps on a ManiaPlanet server.

## Installation
1. Extract the `forcemod` folder at pyplanet/apps/
2. Enable the app as usual in: pyplanet/settings/apps.py
```"apps.mxmod"```
3. Restart pyplanet

## Configuration
You need to add the url of the mod ingame in the pyplanet settings (by typing //settings in the chat) next to `Mod url` then skip the map to apply the mod change.

If the url is empty or invalid, the forced mod is unset.

(Works only on the Stadium environment at the moment)