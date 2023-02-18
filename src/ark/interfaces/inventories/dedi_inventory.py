from typing import Literal, final

from .._button import Button
from .inventory import Inventory


@final
class DedicatedStorageInventory(Inventory):
    """Represents the Dedicated Storage in Ark.

    Extends the abilities of a regular `Inventory` by providing control
    over the additional buttons a dedicated storage adds to the interface.
    """

    _DEPOSIT_ALL = Button((962, 618))
    _WITHDRAW_STACK = Button((962, 660))
    _CLEAR_RESOURCE = Button((962, 703))

    _WITHDRAW_ONE = Button((962, 770))
    _WITHDRAW_FIVE = Button((962, 822))
    _WITHDRAW_TEN = Button((962, 877))

    def __init__(self):
        super().__init__("Tek Dedicated Storage", "assets/wheels/dedi.png")

    def deposit(self) -> None:
        self.click_at(self._DEPOSIT_ALL.location)

    def withdraw_stacks(self, amount: int) -> None:
        for _ in range(amount):
            self.click_at(self._WITHDRAW_STACK.location)

    def withdraw(self, amount: Literal[1, 5, 10], presses: int = 1) -> None:
        buttons = {
            1: self._WITHDRAW_ONE,
            5: self._WITHDRAW_FIVE,
            10: self._WITHDRAW_TEN,
        }
        for _ in range(presses):
            self.click_at(buttons[amount].location)
