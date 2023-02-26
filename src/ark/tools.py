import math

import psutil  # type:ignore[import]

from .items import Item


def ark_is_running() -> bool:
    """Checks if the passed process is running"""
    return "ARK: Survival Evolved" in [
        process.name() for process in psutil.process_iter()
    ]


def close_ark() -> None:
    for process in psutil.process_iter():
        if process.name() == "ARK: Survival Evolved":
            process.kill()


def break_into_components(recipe: dict[Item, int]) -> dict[Item, int]:
    """Computes the total crafting cost of an item taking it's sub
    components into consideration.

    For example, an auto turret costs 140 Metal, 50 paste, 70 electronics...
    But since electronics are a sub component, the total cost would be
    210 Metal, 50 Paste, 210 Silica Pearls...

    The cost is extracted recursively until there are no sub components left.
    Cementing paste is not considered crafted by stone and chitin.
    """
    cost: dict[Item, int] = {}

    def extract_cost(item: Item, amount_needed: int) -> None:
        assert item.recipe is not None

        for item, amount in item.recipe.items():
            if item.recipe is None:
                cost[item] = cost.get(item, 0) + (amount * amount_needed)
            else:
                extract_cost(item, amount)

    for item, amount in recipe.items():
        if item.recipe is None:
            cost[item] = cost.get(item, 0) + amount
        elif amount:
            extract_cost(item, amount)
    return cost


def compute_crafting_plan(
    item_to_craft: Item, available_materials: dict[Item, int]
) -> tuple[int, dict[Item, int], dict[Item, int]]:
    """Computes how many of an item can be crafted given an dictionary of
    available materials. The item must have a `recipe` defined. When computing
    the total possible crafts, crafting sub-components is taken into consideation.

    For example, you may be lacking electronics to craft another item, but you have
    the pearls and the ingots to craft the missing electronics. The sub-components
    that need to be crafted are returned as a dictionary alongside the maximum
    possible amount to craft.

    Parameters
    ----------
    item_to_craft :class:`Item`:
        The item to craft, must define a `recipe`

    available_materials :class:`dict[Item, int]`:
        A dictionary storing the available materials to craft, missing materials
        will be complemented as 0.

    Returns
    -------
    `tuple[int, dict[Item, int], dict[Item, int]]`:
        The maxium number of items that can be crafted, the sub-components
        that need to be crafted and the total cost.
    """
    if item_to_craft.recipe is None:
        raise ValueError(f"{item_to_craft.name} cannot be crafted.")

    available_materials = available_materials.copy()

    cost = {item: 0 for item in item_to_craft.recipe}
    _complement_available_mats(available_materials, item_to_craft.recipe)

    craftable_right_away = _compute_craftable_instantly(
        item_to_craft, available_materials
    )

    for item, amount in item_to_craft.recipe.items():
        can_craft = round(amount * craftable_right_away)
        cost[item] += can_craft
        available_materials[item] -= can_craft

    pcost = cost.copy()
    extra_crafts, sub_components_to_craft = _can_craft(
        item_to_craft, available_materials, cost
    )

    if not extra_crafts:
        cost = pcost

    subcomp_order = list(sub_components_to_craft)
    subcomp_order.sort(key=lambda item: _get_component_depth(item))
    sub_components_to_craft = {k: sub_components_to_craft[k] for k in subcomp_order}

    return (
        math.floor(extra_crafts + craftable_right_away),
        sub_components_to_craft,
        cost,
    )


def _get_component_depth(item: Item, depth=0) -> int:

    if item.recipe is None:
        return depth
    else:
        depth += 1
    for item in item.recipe:
        depth = _get_component_depth(item, depth)
    return depth


def _compute_craftable_instantly(
    item_to_craft: Item, available_materials: dict[Item, int]
) -> int:
    if item_to_craft.recipe is None:
        raise ValueError(f"{item_to_craft.name} cannot be crafted.")

    craftable_right_away = min(
        available_materials[material] / amount
        for material, amount in item_to_craft.recipe.items()
    )
    return math.floor(craftable_right_away)


def _can_craft(
    item: Item,
    available: dict[Item, int],
    cost: dict[Item, int],
    thiscraft=None,
    amount=1,
    components_to_craft=None,
) -> tuple[int, dict[Item, int]]:
    assert item.recipe is not None

    master = components_to_craft is None
    if components_to_craft is None:
        components_to_craft = {}

    crafts = 0
    while True:
        if thiscraft is None or master:
            thiscraft = {}

        for component, amount_needed in item.recipe.items():
            if amount_needed <= available.get(component, 0):
                available[component] -= amount_needed
                thiscraft[component] = thiscraft.get(component, 0) + amount_needed
                continue

            elif component.recipe is None:
                return crafts, components_to_craft

            craftable, _ = _can_craft(
                component,
                available,
                cost,
                thiscraft,
                amount_needed,
                components_to_craft,
            )
            if not craftable or craftable != amount_needed:
                return crafts, components_to_craft
            else:
                components_to_craft[component] = (
                    components_to_craft.get(component, 0) + craftable
                )

        crafts += 1
        if master:
            for material, needed in thiscraft.items():
                cost[material] = cost.get(material, 0) + needed

        if crafts == amount and not master:
            return crafts, components_to_craft


def _complement_available_mats(available: dict, required: dict) -> None:
    available.update({item: 0 for item in set(required) - set(available)})
