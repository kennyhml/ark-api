import pytest

from ark import items, tools


def test_craft_without_subcomponents() -> None:
    available = {items.PASTE: 2000, items.METAL_INGOT: 1500}
    amount, plan, cost = tools.compute_crafting_plan(items.METAL_FOUNDATION, available)
    assert not plan
    assert amount == 30
    assert cost == {items.PASTE: 450, items.METAL_INGOT: 1500}


def test_craft_with_2_layers() -> None:

    available = {
        items.PASTE: 2000,
        items.METAL_INGOT: 1500,
        items.CRYSTAL: 150,
        items.SILICA_PEARL: 2250,
        items.ORGANIC_POLYMER: 500,
    }
    amount, plan, cost = tools.compute_crafting_plan(items.C4_DETONATOR, available)

    assert amount == 15
    assert plan == {items.ELECTRONICS: 750}
    assert cost == {
        items.PASTE: 225,
        items.CRYSTAL: 150,
        items.ELECTRONICS: 0,
        items.METAL_INGOT: 900,
        items.ORGANIC_POLYMER: 300,
        items.SILICA_PEARL: 2250,
    }


def test_craft_2layers_without_subcomponents() -> None:

    available = {
        items.PASTE: 2000,
        items.METAL_INGOT: 1500,
        items.CRYSTAL: 150,
        items.ELECTRONICS: 49,
        items.ORGANIC_POLYMER: 500,
    }
    amount, plan, cost = tools.compute_crafting_plan(items.C4_DETONATOR, available)
    assert not amount
    assert not plan
    assert not any(v for v in cost.values())


def test_raise_error_no_recipe_item() -> None:

    with pytest.raises(ValueError):
        tools.compute_crafting_plan(items.METAL_INGOT, {items.PASTE: 200})


def test_deep_layer_crafting() -> None:
    available = {
        items.METAL_INGOT: 2550,
        items.PASTE: 550,
        items.CRYSTAL: 200,
        items.ELECTRONICS: 70,
        items.SILICA_PEARL: 8000,
        items.ORGANIC_POLYMER: 10000,
        items.AUTO_TURRET: 1,
    }
    amount, plan, cost = tools.compute_crafting_plan(items.HEAVY_AUTO_TURRET, available)

    assert amount == 3
    assert plan == {items.ELECTRONICS: 670, items.AUTO_TURRET: 2}
    assert cost == {
        items.PASTE: 550,
        items.ELECTRONICS: 70,
        items.METAL_INGOT: 2150,
        items.ORGANIC_POLYMER: 190,
        items.SILICA_PEARL: 2010,
        items.AUTO_TURRET: 1,
    }

    available[items.AUTO_TURRET] = 0
    available[items.PASTE] = 600

    amount, plan, cost = tools.compute_crafting_plan(items.HEAVY_AUTO_TURRET, available)
    assert amount == 3
    assert plan == {items.ELECTRONICS: 740, items.AUTO_TURRET: 3}
    assert cost == {
        items.PASTE: 600,
        items.ELECTRONICS: 70,
        items.METAL_INGOT: 2360,
        items.ORGANIC_POLYMER: 210,
        items.SILICA_PEARL: 2220,
        items.AUTO_TURRET: 0,
    }


def test_amount_flattened() -> None:
    available = {
        items.SILICA_PEARL: 5211,
        items.PASTE: 2600,
        items.METAL_INGOT: 8757,
        items.ELECTRONICS: 1100,
        items.CRYSTAL: 10000,
        items.HIDE: 20000,
        items.ORGANIC_POLYMER: 10000,
    }

    amount, plan, cost = tools.compute_crafting_plan(items.HEAVY_AUTO_TURRET, available)
    assert amount == 10
    assert plan == {items.AUTO_TURRET: 10, items.ELECTRONICS: 1620}
    assert cost == {
        items.PASTE: 2000,
        items.ELECTRONICS: 1080,
        items.METAL_INGOT: 7020,
        items.ORGANIC_POLYMER: 700,
        items.SILICA_PEARL: 4860,
        items.AUTO_TURRET: 0,
    }

def test_tek_turret() -> None:
    available = {
        items.SILICA_PEARL: 5211,
        items.PASTE: 2600,
        items.METAL_INGOT: 8757,
        items.ELECTRONICS: 1100,
        items.CRYSTAL: 10000,
        items.HIDE: 20000,
        items.ORGANIC_POLYMER: 10000,
        items.ELEMENT: 18
    }
    amount, plan, cost = tools.compute_crafting_plan(items.TEK_TURRET, available)
    assert amount == 6
    assert not plan
    assert cost == {
        items.PASTE: 300,
        items.ELECTRONICS: 600,
        items.METAL_INGOT: 600,
        items.ORGANIC_POLYMER: 300,
        items.ELEMENT: 18
    }