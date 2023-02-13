from typing import Literal, overload


from ark.exceptions import NoItemsDepositedError

from ..interfaces.inventories import DedicatedStorageInventory
from ..items import Item
from .structure import Structure


class TekDedicatedStorage(Structure):
    """Represents the grinder inventory in ark.

    Is able to be turned on and off and grind all.
    """

    TRANSFERRED_REGION = (710, 4, 460, 130)
    ITEM_ADDED_REGION = (0, 430, 160, 350)

    def __init__(self) -> None:
        super().__init__("Tek Dedicated Storage", "dedi", DedicatedStorageInventory())

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
            if not self.find_item_deposited(item):
                continue

            # 5 attempts to get a better chance for a good result
            for _ in range(5):
                if amount := self._get_amount_deposited(item):
                    return item, amount
        return item, 0

    def is_in_deposit_range(self) -> bool:
        """Returns whether the dedicated storage is currently within the
        depositing range of the player."""
        return (
            self.window.locate_template(
                "templates/deposit_all.png",
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
                "templates/items_deposited.png",
                region=self.TRANSFERRED_REGION,
                confidence=0.75,
            )
            is not None
        )

    def _attempt_deposit(self) -> None:
        """Presses the 'E' key on a dedi until the deposit text appears.

        Raises a `NoItemsDepositedError` if we were unable to deposit within
        30 seconds.
        """
        self.sleep(0.5)
        self.press(self.keybinds.use)
        c = 0

        while not self.deposited_items():
            self.sleep(0.1)
            c += 1
            # retry every 3 seconds
            if c % 30 == 0:
                self.press(self.keybinds.use)

            if c > 300:
                raise NoItemsDepositedError("Failed to deposit after 30 seconds!")