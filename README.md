# ark-api
ark-api is an easy to use, fully open-source package to help you automate tasks in [Ark: Survival Evolved](https://ark.fandom.com/wiki/ARK:_Survival_Evolved).

## Installation
ark-api is is available on pypi and can be downloaded using pip, note that python 3.10+ is required.
```py
pip install ark-api
```

## Features
- Pythonic representations of various in-game objects.
- Full control over the player movements.
- Reading of in-game settings / keybinds from ark .ini files.
- Server queries for server status, day, IP, port..
- Item representations (and the recipes to craft them)
- Tools to calculate the maximum amount of items craftable with a map of materials
- Lots of control over inventory interactions
- Grabbing of the ark boundaries / scaling to resolution

# Examples
Alot of examples how to use the ark-api can be found in the [ark-gacha-bot](https://github.com/kennyhml/ark-gacha-bot) I am providing, as it is heavily based on the ark-api.

## First steps
First, we need to set the path to the ark directory, so it can load the .ini files.
```py
from ark import config

config.ARK_PATH = "C:\..."
```
## Controlling the player
```py
from ark import Player

player = Player(health=300, weight=800, food=100, water=100)

# turning the player
player.turn_x_by(90)
player.turn_y_by(-20)

# walking with the player
player.walk("w", duration=2)
```
## Making a small script
Let's make a small script to automate the process of filling a forge with metal from a dedicated storage!
```py
from ark import Player, TekDedicatedStorage, IndustrialForge, items

player = Player(300, 800, 100, 100)
dedi = TekDedicatedStorage()
forge = IndustrialForge()

dedi.open()
dedi.transfer_all()
dedi.close()

player.turn_x_by(100, delay=0.5)
forge.open()
player.transfer_all(items.RAW_METAL)
forge.turn_on()
forge.close()
```





