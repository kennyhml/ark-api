"""
dedi inventory
"""
from .inventory import Inventory

class DedicatedStorageInventory(Inventory):
    """Represents the Dedicated Storage Box in ark.

    Contains dedi specific methods such as depositing.

    TO-DO: Add methods for withdrawing.
    """

    def __init__(self):
        super().__init__("Tek Dedicated Storage", "dedi")


    def withdraw_stacks(self, stacks: int) -> None:
        for _ in range(stacks):
            self.click_at(966, 660)

    def withdraw_one(self, amount: int) -> None:
        for _ in range(amount):
            self.click_at(962, 766)
