"""
Ark API module representing the players inventory.
"""
import math
from typing import Optional, final

import pyautogui as pg  # type: ignore[import]

from ..._tools import await_event
from ...exceptions import InventoryNotAccessibleError, NoItemsAddedError
from ...items import Item
from .._button import Button
from .inventory import Inventory


class PlayerInventory(Inventory):
    """Represents the player inventory in ark.

    Provides the ability to implement player inventory related actions
    such as transferring items to other inventories.

    Inherits from the `Inventory` class.
    """

    SLOTS = [
        (x + 47, y + 47) for y in range(232, 883, 93) for x in range(117, 582 + 93, 93)
    ]

    _CREATE_FOLDER = Button((513, 189))
    _TRANSFER_ALL = Button((350, 180))
    _DROP_ALL = Button((400, 180))
    _INVENTORY_TAB = Button((199, 117), (110, 90, 180, 60), "inventory.png")
    _CRAFTING_TAB = Button((1716, 118))

    _SEARCHBAR = (180, 180)
    _ADDED_REGION = (10, 1000, 220, 80)
    _ITEM_REGION = (117, 232, 582, 883)

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
        if not await_event(self.received_item, max_duration=30):
            raise NoItemsAddedError(item.name if isinstance(item, Item) else item)

    def transfer_amount(
        self, item: Item, amount: int, target_inventory: Optional[Inventory] = None
    ) -> None:
        """Transfers the amount of the given item into the target inventory.
        If the amount divided by the item stacksize is greater than 40,
        the amount transferred will be OCRd and validated, which is fairly accurate.

        Else, after each transfer it checks how many stacks of the item are in the
        target inventory and multiplies it by the item stacksize, which is very
        accurate.
        
        Parameters:
        -----------
        item :class:`str`:
            The item to search for before transferring

        amount :class:`int`:
            The quantity of items to be transferred

        target_inventory :class:`Inventory`: [Optional]
            The inventory to transfer the items to
        """
        # make sure we dont transfer any other items
        self.search_for(item)

        # get total row transfers, add a little buffer for lag (1.5 by default)
        total_transfers = round(
            (int(math.ceil(amount / 100.0)) * 100 / item.stack_size) / 6 * 2
        )

        count_by_stacks = (amount / item.stack_size) < 40
        if count_by_stacks and target_inventory:
            target_inventory.search_for(item)

        transferred = 0
        # transfer the items
        for _ in range(total_transfers):
            if not self.has_item(item):
                return

            for pos in [(167 + (i * 95), 282) for i in range(6)]:
                pg.moveTo(pos)
                pg.press("t")
                self.sleep(0.2)

                if count_by_stacks and target_inventory:
                    transferred = target_inventory.count_item(item) * item.stack_size
                else:
                    # OCR the total amount transferred, None if undetermined
                    transferred = self.get_amount_transferred(item, "rm")
                    if not transferred:
                        continue

                # if the amount of items we transferred makes sense we can cancel
                if amount <= transferred <= amount + 3000:
                    return

    def transfer_all(self, inventory: Inventory, item: Optional[Item | str] = None):
        """Transfers all of the given item into the target inventory

        Parameters:
        -----------
        inventory: :class:`Inventory`:
            The inventory to receive the items

        item: :class:`Item`:
            The item to search for
        """
        if not inventory.is_open():
            return

        if item:
            self.search_for(item)
        self.click_transfer_all()

    def pellets_left_to_tranfer(self) -> bool:
        """Checks if there are any pellets left to even transfer,
        we wouldnt wanna waste time clicking empty slots RIGHT @SLEEPY!!?"""
        return (
            self.window.locate_template(
                "assets/items/pellet.png",
                region=(116, 700, 95, 90),
                confidence=0.8,
            )
            is not None
        )

    def take_pellets(self, transfer_back: int = 8) -> bool:
        """Transfers some pellets into another inventory, likely a Gacha."""
        # ensure we even have pellets to transfer
        if not self.pellets_left_to_tranfer():
            return False

        # start transferring pellets, keep track of rows
        self.click_at(167, 745)
        rows = 0
        for _ in range(transfer_back):
            for i in range(6):
                self.move_to(167 + (i * 95), 745)
                pg.press("t")

            rows += 1
            # check again if we ran out of pellets yet
            if not self.pellets_left_to_tranfer():
                break
        return True
