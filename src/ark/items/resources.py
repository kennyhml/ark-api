from ctypes.wintypes import CHAR
from .item import Item

DUST = Item(
    name="Element Dust",
    search_name="dust",
    stack_size=1000,
    inventory_icon="assets/items/resources/dust.png",
    added_icon="assets/items/dust_deposited.png",
    added_text="assets/items/dust_text.png",
)

BLACK_PEARL = Item(
    name="Black Pearl",
    search_name="black",
    stack_size=200,
    inventory_icon="assets/items/resources/black_pearl.png",
    added_icon="assets/items/black_pearl_deposited.png",
    added_text="assets/items/black_pearl_text.png",
)

CRYSTAL = Item(
    name="Crystal",
    search_name="crystal",
    stack_size=100,
    inventory_icon="assets/items/resources/crystal.png",
)

GREENGEM = Item(
    name="Fragmented Green Gem",
    search_name="green gem",
    stack_size=100,
    inventory_icon="assets/items/resources/green_gem.png",
)

SAND = Item(
    name="Sand",
    search_name="sand",
    stack_size=100,
    inventory_icon="assets/items/resources/sand.png",
)

THATCH = Item(
    name="Thatch",
    search_name="thatch",
    stack_size=200,
    inventory_icon="assets/items/resources/thatch.png",
)

BLUEGEM = Item(
    name="Blue Crystalized Sap",
    search_name="blue",
    stack_size=100,
    inventory_icon="assets/items/resources/blue_gem.png",
)

SILK = Item(
    name="Silk",
    search_name="silk",
    stack_size=200,
    inventory_icon="assets/items/resources/silk.png",
)

CLAY = Item(
    name="Clay",
    search_name="clay",
    stack_size=100,
    inventory_icon="assets/items/resources/clay.png",
)

OIL = Item(
    name="Oil",
    search_name="oil",
    stack_size=100,
    inventory_icon="assets/items/resources/oil.png",
)

GASBALL = Item(
    name="Congealed Gas Balls",
    search_name="gas ball",
    stack_size=100,
    inventory_icon="assets/items/resources/gasball.png",
)

SULFUR = Item(
    name="Sulfur",
    search_name="sulfur",
    stack_size=100,
    inventory_icon="assets/items/resources/sulfur.png",
)

METAL = Item(
    name="Metal",
    search_name="metal",
    stack_size=200,
    inventory_icon="assets/items/resources/metal.png",
)

REDGEM = Item(
    name="Red Crystalized Sap",
    search_name="red",
    stack_size=100,
    inventory_icon="assets/items/resources/red_gem.png",
)

OBSIDIAN = Item(
    name="Obsidian",
    search_name="obsidian",
    stack_size=100,
    inventory_icon="assets/items/resources/obsidian.png",
)

SAP = Item(
    name="Sap",
    search_name="sap",
    stack_size=100,
    inventory_icon="assets/items/resources/sap.png",
)

METAL_INGOT = Item(
    name="Ingot",
    search_name="ingot",
    stack_size=300,
    inventory_icon="assets/items/resources/metal_ingot.png",
    added_icon="assets/items/ingot_icon.png",
    added_text="assets/items/ingot_text.png",
)

FLINT = Item(
    name="Flint",
    search_name="flint",
    stack_size=100,
    inventory_icon="assets/items/resources/flint.png",
)

STONE = Item(
    name="Stone",
    search_name="stone",
    stack_size=100,
    inventory_icon="assets/items/resources/stone.png",
    added_icon="assets/items/stone_icon.png",
    added_text="assets/items/stone_text.png",
)

FUNGAL_WOOD = Item(
    name="Fungal wood",
    search_name="wood",
    stack_size=100,
    inventory_icon="assets/items/resources/fungal_wood.png",
)

PASTE = Item(
    name="Paste",
    search_name="paste",
    stack_size=100,
    inventory_icon="assets/items/resources/paste.png",
    added_icon="assets/items/paste_icon.png",
    added_text="assets/items/paste_text.png",
)

SILICA_PEARL = Item(
    name="Silica Pearl",
    search_name="pearls",
    stack_size=100,
    inventory_icon="assets/items/resources/silica_pearl.png",
    added_icon="assets/items/pearls_icon.png",
    added_text="assets/items/pearls_text.png",
)

HIDE = Item(
    name="Hide",
    search_name="hide",
    stack_size=200,
    inventory_icon="assets/items/resources/hide.png",
)

HARD_POLYMER = Item(
    name="Polymer",
    search_name="poly",
    stack_size=100,
    inventory_icon="assets/items/resources/polymer.png",
)

ORGANIC_POLYMER = Item(
    name="Organic Polymer",
    search_name="poly",
    stack_size=20,
    inventory_icon="assets/items/resources/organic_polymer.png",
)

GASOLINE = Item(
    name="Gasoline",
    search_name="gasoline",
    stack_size=100,
    inventory_icon="assets/items/resources/gasoline.png",
)

CHARCOAL = Item(
    name="Charcoal",
    search_name="coal",
    stack_size=100,
    inventory_icon="assets/items/resources/charcoal.png",
)

SPARKPOWDER = Item(
    name="Sparkpowder",
    search_name="spark",
    recipe={FLINT: 2, STONE: 1},
    stack_size=100,
    inventory_icon="assets/items/resources/sparkpowder.png",
)

GUNPOWDER = Item(
    name="Gunpowder",
    search_name="gunpowder",
    recipe={SPARKPOWDER: 1, CHARCOAL: 1},
    stack_size=100,
    inventory_icon="assets/items/resources/gunpowder.png",
)

ARB = Item(
    name="Advanced Rifle Bullet",
    search_name="advanced rifle bullet",
    stack_size=100,
    inventory_icon="assets/items/resources/arb.png",
    added_icon="assets/items/arb_icon.png",
    added_text="assets/items/arb_text.png",
)

ANGLER_GEL = Item(
    name="Angler Gel",
    search_name="gel",
    stack_size=100,
    inventory_icon="assets/items/resources/angler_gel.png",
)

FIBER = Item(
    name="Fiber",
    search_name="fiber",
    stack_size=300,
    inventory_icon="assets/items/resources/fiber.png",
)

WOOD = Item(
    name="Wood",
    search_name="wood",
    stack_size=100,
    inventory_icon="assets/items/resources/wood.png",
)

Y_TRAP = Item(
    name="Y Trap",
    search_name="trap",
    stack_size=10,
    inventory_icon="assets/items/resources/ytrap.png",
    added_text="assets/items/y_trap_added.png",
    added_icon="assets/items/plant_species_y_trap.png",
)

GACHA_CRYSTAL = Item(
    name="Gacha Crystal",
    search_name="gacha",
    stack_size=1,
    inventory_icon="assets/items/resources/gacha_crystal.png",
)

ELECTRONICS = Item(
    name="Electronics",
    search_name="electronics",
    stack_size=100,
    recipe={SILICA_PEARL: 3, METAL_INGOT: 1},
    inventory_icon="assets/items/resources/electronics.png",
    added_icon="assets/items/electronics_icon.png",
    added_text="assets/items/electronics_text.png",
)

ELEMENT = Item(
    name="Element",
    search_name="element",
    stack_size=100,
    inventory_icon="assets/items/resources/element.png",
)