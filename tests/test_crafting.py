import pytest

from ark import items, tools


def test_craft_without_subcomponents() -> None:
    available = {items.PASTE: 2000, items.METAL_INGOT: 1500}
    amount, plan = tools.compute_crafting_plan(items.METAL_FOUNDATION, available)
    assert not plan
    assert amount == 30


def test_craft_with_2_layers() -> None:

    available = {
        items.PASTE: 2000,
        items.METAL_INGOT: 1500,
        items.CRYSTAL: 150,
        items.SILICA_PEARL: 2250,
        items.ORGANIC_POLYMER: 500,
    }
    amount, plan = tools.compute_crafting_plan(items.C4_DETONATOR, available)

    assert amount == 15
    assert plan == {items.ELECTRONICS: 750}


def test_craft_2layers_without_subcomponents() -> None:

    available = {
        items.PASTE: 2000,
        items.METAL_INGOT: 1500,
        items.CRYSTAL: 150,
        items.ELECTRONICS: 49,
        items.ORGANIC_POLYMER: 500,
    }
    amount, plan = tools.compute_crafting_plan(items.C4_DETONATOR, available)
    assert not amount
    assert not plan


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
    amount, plan = tools.compute_crafting_plan(items.HEAVY_AUTO_TURRET, available)

    assert amount == 3
    assert plan == {items.ELECTRONICS: 670, items.AUTO_TURRET: 2}

    available[items.AUTO_TURRET] = 0
    available[items.PASTE] = 600

    amount, plan = tools.compute_crafting_plan(items.HEAVY_AUTO_TURRET, available)
    assert amount == 3
    assert plan == {items.ELECTRONICS: 740, items.AUTO_TURRET: 3}
