from typing import Literal, final, overload

from ark.exceptions import InventoryNotAccessibleError, NoItemsDepositedError

from ..._helpers import await_event
from ...items import Item
from ..inventories import DedicatedStorageInventory
from .structure import Structure
from ...config import TIMER_FACTOR


@final
class TekDedicatedStorage(Structure):
    """Represents the Tek Storage in Ark.

    Extends the abilities a regular `Structure` provides by adding
    deposit-interaction related methods.
    """

    _TRANSFERRED_REGION = (710, 4, 460, 130)
    _ITEM_ADDED_REGION = (0, 430, 160, 350)

    def __init__(self) -> None:
        super().__init__("Tek Dedicated Storage", "assets/wheels/dedi.png")
        self.inventory: DedicatedStorageInventory = DedicatedStorageInventory()

    @overload
    def deposit(self, items: list[Item], get_amount: Literal[False]) -> None:
        ...

    @overload
    def deposit(self, items: list[Item], get_amount: Literal[True]) -> tuple[Item, int]:
        ...

    def deposit(self, items: list[Item], get_amount: bool) -> tuple[Item, int] | None:
        """Attempts to deposit into a dedi until the 'x items deposited.'
        green message appears up top where x can be any number.

        Parameters:
        -----------
        items :class:`list`:
            A list of items where each item is a possibly deposited item

        Returns:
        -----------
        item :class:`str`: [Optional]
            The name of the item that was being deposited or was last checked

        amount :class:`int`: [Optional]
            The quantity of items that were deposited, 0 if none.

        Raises:
        -----------
        `NoItemsDepositedError` if the expected text did not appear after 30 seconds.
        """
        # wait for text from possibly prior attempts to go away
        while self.deposited_items():
            self.sleep(0.1)

        self._attempt_deposit()
        if not get_amount:
            return None

        # correct wrong items arg type
        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not self._find_item_deposited(item):
                continue

            print(f"{item.name} was deposited...")
            self.sleep(0.3)
            for _ in range(5):
                if amount := self._get_amount_deposited(item):
                    return item, amount
                self.sleep(0.1)
        return item, 0

    def can_be_opened(self) -> bool:
        """Checks if the dedi can be opened by attempting to do so"""
        try:
            self.inventory.open(max_duration=3)
        except InventoryNotAccessibleError:
            return False
        self.close()
        return True

    def is_in_deposit_range(self) -> bool:
        """Returns whether the dedicated storage is currently within the
        depositing range of the player."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/deposit_all.png",
                region=(0, 0, 1920, 1080),
                confidence=0.7,
            )
            is not None
        )

    def deposited_items(self) -> bool:
        """Returns whether an item has been deposited, determined by the green
        'x items transferred' text on top of the screen."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/items_deposited.png",
                region=self._TRANSFERRED_REGION,
                confidence=0.75,
            )
            is not None
        )

    def _attempt_deposit(self) -> None:
        """Presses the 'E' key on a dedi until the deposit text appears.

        Raises a `NoItemsDepositedError` if we were unable to deposit within
        30 seconds.
        """
        attempts = 0
        while not self.deposited_items():
            self.press(self.keybinds.use)
            if await_event(self.deposited_items, max_duration=3):
                return

            attempts += 1
            if attempts >= (10 * TIMER_FACTOR):
                raise NoItemsDepositedError(self.inventory)
