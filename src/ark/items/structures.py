from .item import Item
from .resources import ELECTRONICS, METAL_INGOT, ORGANIC_POLYMER, PASTE, ELEMENT

AUTO_TURRET = Item(
    name="Auto Turret",
    search_name="auto turret",
    recipe={PASTE: 50, ELECTRONICS: 70, METAL_INGOT: 140, ORGANIC_POLYMER: 20},
    stack_size=1,
    inventory_icon="assets/items/structures/auto_turret.png",
)

HEAVY_AUTO_TURRET = Item(
    name="Heavy Auto Turret",
    search_name="heavy",
    stack_size=1,
    inventory_icon="assets/items/structures/heavy_auto_turret.png",
    recipe={
        PASTE: 150,
        ELECTRONICS: 200,
        METAL_INGOT: 400,
        ORGANIC_POLYMER: 50,
        AUTO_TURRET: 1,
    },
)

TEK_TURRET = Item(
    name="Tek Turret",
    search_name="tek turret",
    stack_size=1,
    inventory_icon="assets/items/structures/tek_turret.png",
    recipe={
        PASTE: 50,
        ELECTRONICS: 100,
        METAL_INGOT: 100,
        ELEMENT: 3,
        ORGANIC_POLYMER: 50,
    },

)

BEHEMOTH_GATEWAY = Item(
    name="Behemoth Gateway",
    search_name="behemoth",
    stack_size=100,
    inventory_icon="assets/items/structures/behemoth_gateway.png",
)

BEHEMOTH_GATE = Item(
    name="Behemoth Gate",
    search_name="behemoth",
    stack_size=100,
    inventory_icon="assets/items/structures/behemoth_gate.png",
)

TREE_PLATFORM = Item(
    name="Tree Platform",
    search_name="tree",
    stack_size=100,
    inventory_icon="assets/items/structures/tree_platform.png",
)

CROP_PLOT = Item(
    name="Large Crop Plot",
    search_name="crop",
    stack_size=100,
    inventory_icon="assets/items/structures/crop_plot.png",
)

RESERVOIR = Item(
    name="Metal Water Reservoir",
    search_name="reservoir",
    stack_size=100,
    inventory_icon="assets/items/structures/reservoir.png",
)

WARDRUMS = Item(
    name="Wardrums",
    search_name="wardrum",
    stack_size=100,
    inventory_icon="assets/items/structures/wardrum.png",
)

METAL_FOUNDATION = Item(
    name="Metal Foundation",
    search_name="metal foundation",
    stack_size=100,
    inventory_icon="assets/items/structures/metal_foundation.png",
    recipe={METAL_INGOT: 50, PASTE: 15},
)

METAL_TRIANGLE = Item(
    name="Metal Triangle Foundation",
    search_name="metal triangle foundation",
    stack_size=100,
    inventory_icon="assets/items/structures/metal_triangle.png",
    recipe={METAL_INGOT: 25, PASTE: 8},
)

METAL_GATEWAY = Item(
    name="Metal Gateway",
    search_name="gateway",
    stack_size=100,
    inventory_icon="assets/items/structures/metal_gateway.png",
    recipe={METAL_INGOT: 170, PASTE: 50},
)

METAL_GATE = Item(
    name="Metal Gate",
    search_name="gate",
    stack_size=100,
    inventory_icon="assets/items/structures/metal_gate.png",
    recipe={METAL_INGOT: 35, PASTE: 10},
)
