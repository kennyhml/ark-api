import math
import random
from typing import Optional, final

import pyautogui as pg  # type: ignore[import]

from ... import config
from ..._helpers import await_event, get_center
from ...exceptions import (InventoryNotAccessibleError, MissingItemErrror,
                           NoItemsAddedError)
from ...items import Item
from .._button import Button
from .inventory import Inventory


@final
class PlayerInventory(Inventory):
    """Represents the player inventory in ark.

    Extends the abiliy of a regular `Inventory` by adding methods
    responsible for transferring items from the own inventory into
    a target inventory, as well as adjusting the region boundaries
    in order to apply the same methods to the player inventory that the
    `Inventory` already provides.
    """

    SLOTS = [
        (x, y, 93, 93) for y in range(232, 883, 93) for x in range(117, 582 + 93, 93)
    ]
    HEAD = (750, 155, 94, 94)
    TORSO = (750, 252, 94, 94)
    LEGS = (750, 349, 94, 94)
    HANDS = (1076, 155, 94, 94)
    OFFHAND = (1076, 252, 94, 94)
    FEET = (1076, 349, 94, 94)

    _CREATE_FOLDER = Button((513, 189))
    _TRANSFER_ALL = Button((350, 180))
    _DROP_ALL = Button((400, 180))
    _INVENTORY_TAB = Button((199, 117), (110, 90, 180, 60), "inventory.png")
    _CRAFTING_TAB = Button((1716, 118), (1627, 82, 211, 69), "crafting.png")

    _SEARCHBAR = (180, 180)
    _ADDED_REGION = (10, 1000, 220, 80)
    _ITEM_REGION = (117, 232, 582, 883)
    _UPPER_ITEM_REGION = (117, 230, 568, 191)
    _CAPPED_ICON = (85, 235, 52, 50)
    _YOU = (794, 116)

    def __init__(self):
        super().__init__("Player")

    def open(self, *_) -> None:
        """Opens the player inventory using the specified keybind.

        If the inventory did not open after 30 seconds,
        an `InventoryNotAccessibleError` is raised.
        """
        attempts = 0
        while not self.is_open():
            self.press(self.keybinds.inventory)
            if await_event(self.is_open, max_duration=5):
                return

            attempts += 1
            if attempts >= 6:
                raise InventoryNotAccessibleError(self._name)

    def await_items_added(self, item: Item | str) -> None:
        """Waits for items to be added to the inventory"""
        if not await_event(self.received_item, max_duration=30 * config.TIMER_FACTOR):
            raise NoItemsAddedError(item.name if isinstance(item, Item) else item)

    def transfer(
        self, item: Item, amount: int, target: Optional[Inventory] = None
    ) -> None:
        """Transfers an amount of an item into an inventory. The method used
        to transfer the items depends on the amount of stacks that has to be
        transferred, how many are already in the target inventory, and whether
        a target inventory was given to begin with.

        If more than 40 stacks of items need to be transferred, additionally
        to what is already within the target, or no target inventory was given,
        it will simply iterate over the top row of items and OCR the amount
        of items removed.

        Otherwise, we can check on the amount of stacks in the target before
        transferring and compare them to after, for each item. This way we can
        accurately count the items transferred while being more lag proof.

        Parameters:
        -----------
        item :class:`str`:
            The item to search for before transferring

        amount :class:`int`:
            The quantity of items to be transferred

        target_inventory :class:`Inventory`: [Optional]
            The inventory to transfer the items to, required for stack transferring
        """
        self.search(item)
        # round the amount to the next stacksize, i.e if 403 items are to
        # be transferred, and the stacksize is 200, it will be rounded to 600
        amount = int(math.ceil(amount / item.stack_size)) * item.stack_size
        stacks = int(amount / item.stack_size)
        rows = round(stacks / 6)

        if rows > 7 or not target:
            self._transfer_by_rows(item, rows)
            return

        # search the item in the target so we can track how much we already
        # transferred. Before that check that it actually has the slots free
        # we need, if not we need to go back to doing it by row.
        target.search(item)
        self.sleep(0.3)

        stacks_in_target = target.count(item)
        if (stacks_in_target + stacks) > 42:
            self._transfer_by_rows(item, rows)
            return

        if stacks_in_target == stacks:
            return

        self._transfer_by_stacks(item, stacks, target)

    def equip(self, item: Item) -> None:
        self.search(item)
        self.sleep(0.3)

        pos = self.find(item)
        if pos is None:
            raise MissingItemErrror(item.name)

        before = self.count(item)
        self.click_at(self._YOU, delay=0.2)
        self.click_at(pos)
        self.press(self.keybinds.use)

        if not await_event(
            lambda: before != self.count(item),
            max_duration=30 * config.TIMER_FACTOR,
            ignore_annotation=True,
        ):
            raise TimeoutError

    def unequip(self, item: Item) -> None:
        self.click_at(self._YOU, delay=0.2)
        for slot in [
            self.HEAD,
            self.TORSO,
            self.LEGS,
            self.HANDS,
            self.OFFHAND,
            self.FEET,
        ]:
            if not self._slot_has_item(slot, item):
                continue
            self.click_at(get_center(slot))
            self.press(self.keybinds.use)

            if not await_event(
                lambda: self._slot_has_item(slot, item),
                False,
                max_duration=30 * config.TIMER_FACTOR,
                ignore_annotation=True,
            ):
                raise TimeoutError
            return
        raise MissingItemErrror(item.name)

    def transfer_spam(self, item: Item, times: int) -> None:
        self.search(item)

        for _ in range(times):
            slot = random.choice(self.SLOTS)
            self.move_to(get_center(slot))
            self.press(self.keybinds.transfer)

    def hp_full(self) -> bool:
        return pg.pixelMatchesColor(*(1118, 514), (15, 166, 181), tolerance=40)

    def food_full(self) -> bool:
        return pg.pixelMatchesColor(*(1118, 643), (15, 166, 181), tolerance=40)

    def water_full(self) -> bool:
        return pg.pixelMatchesColor(*(1118, 685), (15, 166, 181), tolerance=40)

    def _slot_has_item(self, slot: tuple[int, int, int, int], item: Item) -> bool:
        return (
            self.window.locate_template(
                item.inventory_icon, slot, confidence=0.7, grayscale=True
            )
            is not None
        )

    def _transfer_by_stacks(self, item: Item, stacks: int, target: Inventory) -> None:
        """Internal implementation of the stack transferring technique.

        Counts the amount of items before pressing 'T' and waits for it to
        change after the press.
        """
        amount = item.stack_size * stacks

        for _ in range(stacks):
            slot = self.find(item)
            if slot is None:
                return

            pg.moveTo(slot)
            before = target.count(item)
            self.press(self.keybinds.transfer)

            target._receive_stack(item, before)
            transferred = target.count(item) * item.stack_size

            print(f"Transferred {transferred}/{amount}...")
            if amount <= transferred <= amount + 3000:
                return

    def _transfer_by_rows(self, item: Item, rows: int) -> None:
        """Internal implementation of the row transferring technique.

        OCRs the amount transferred after each row
        """
        EXTRA_ITERATION_FACTOR = 1.5
        amount = item.stack_size * (rows * 6)

        for _ in range(round(rows * EXTRA_ITERATION_FACTOR) * 6):
            slot = self.find(item)
            if slot is None:
                return

            pg.moveTo(slot)
            self.press(self.keybinds.transfer)
            transferred = self.get_amount_transferred(item, "rm")
            if not transferred:
                continue

            print(f"Transferred {transferred}/{amount}...")
            if amount <= transferred <= (amount + 10 * item.stack_size):
                return
