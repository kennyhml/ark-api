from .item import Item
from .resources import PASTE, METAL_INGOT, CRYSTAL, ELECTRONICS, ORGANIC_POLYMER

ASSAULT_RIFLE = Item(
    name="Assault Rifle",
    search_name="ass",
    stack_size=1,
    inventory_icon="assets/items/weapons/assault_rifle.png",
)

PUMPGUN = Item(
    name="Pump-Action Shotgun",
    search_name="pump",
    stack_size=1,
    inventory_icon="assets/items/weapons/pumpgun.png",
)

SHOTGUN = Item(
    name="Shotgun",
    search_name="shotgun",
    stack_size=1,
    inventory_icon="assets/items/weapons/shotgun.png",
)

FABRICATED_SNIPER = Item(
    name="Fabricated Sniper Rifle",
    search_name="sniper",
    stack_size=1,
    inventory_icon="assets/items/weapons/fabricated_sniper.png",
)

FABRICATED_PISTOL = Item(
    name="Fabricated Pistol",
    search_name="pistol",
    stack_size=1,
    inventory_icon="assets/items/weapons/fabricated_pistol.png",
)

LONGNECK = Item(
    name="Longneck",
    search_name="longneck",
    stack_size=1,
    inventory_icon="assets/items/weapons/longneck.png",
)

SIMPLE_PISTOL = Item(
    name="Simple Pistol",
    search_name="simple",
    stack_size=1,
    inventory_icon="assets/items/weapons/simple_pistol.png",
)

SWORD = Item(
    name="Sword",
    search_name="sword",
    stack_size=1,
    inventory_icon="assets/items/weapons/sword.png",
)

PIKE = Item(
    name="Pike",
    search_name="pike",
    stack_size=1,
    inventory_icon="assets/items/weapons/pike.png",
)

HATCHET = Item(
    name="Metal Hatchet",
    search_name="hatchet",
    stack_size=1,
    inventory_icon="assets/items/weapons/hatchet.png",
)

PICK = Item(
    name="Metal Pick",
    search_name="pick",
    stack_size=1,
    inventory_icon="assets/items/weapons/pick.png",
)

TORCH = Item(
    name="Torch",
    search_name="torch",
    stack_size=1,
    inventory_icon="assets/items/weapons/torch.png",
)

CROSSBOW = Item(
    name="Crossbow",
    search_name="crossbow",
    stack_size=1,
    inventory_icon="assets/items/weapons/crossbow.png",
)

BOW = Item(
    name="bow",
    search_name="bow",
    stack_size=1,
    inventory_icon="assets/items/weapons/bow.png",
)

C4_DETONATOR = Item(
    name="C4 Remote Detonator",
    search_name="det",
    stack_size=1,
    inventory_icon="assets/items/weapons/c4_detonator.png",
    recipe={
        PASTE: 15,
        CRYSTAL: 10,
        ELECTRONICS: 50,
        METAL_INGOT: 10,
        ORGANIC_POLYMER: 20,
    },
)

ROCKET_LAUNCHER = Item(
    name="Rocket Launcher",
    search_name="rocket launcher",
    stack_size=1,
    inventory_icon="assets/items/weapons/rocket_launcher.png",
    recipe={
        PASTE: 60,
        METAL_INGOT: 50,
        ORGANIC_POLYMER: 80,
    },
)
