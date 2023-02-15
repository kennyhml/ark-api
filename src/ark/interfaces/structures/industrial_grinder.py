from typing import final

from ...items import FLINT, Item
from .._button import Button
from .structure import Structure


@final
class IndustrialGrinder(Structure):
    """Represents the Industrial Grinder in Ark.

    The industrial grinder extends the abilities the `Structure` class
    by adding methods to grind it's contents or specific items. For automation
    purposes the grinder plays a big role for easy polymer access.

    Beware that, while you may consider polymer, paste, ingots or pearls
    to be craftables of the `Industrial Grinder`, they are not considered as such.

    It is defined as a toggleable, but items that are a result of a grinding
    session should not be considered crafted. Chitin, flint, thatch and stone
    however are considered craftables, as they can be crafted through an engram.
    """

    GRIND_ALL = Button((969, 663), (740, 570, 444, 140), "grind_all_items.png")
    GRIND_STACK = Button((963, 701))

    def __init__(self) -> None:
        super().__init__(
            name="Industrial Grinder",
            action_wheel="assets/wheels/industrial_grinder.png",
            craftables=[FLINT],
            toggleable=True,
        )

    def can_grind(self) -> bool:
        """Checks if the grinder can grind"""
        return self.inventory.locate_button(self.GRIND_ALL, confidence=0.85)

    def grind_all(self) -> bool:
        """Presses the grind all button if it is available.
        Returns whether items got grinded or not.
        """
        if not self.can_grind():
            return False

        self.click_at(self.GRIND_ALL.location, delay=0.3)
        return True

    def grind_one(self, item: Item) -> None:
        if (pos := self.inventory.find(item)) is None:
            return

        self.click_at(pos, delay=0.3)
        self.click_at(self.GRIND_STACK.location, delay=0.3)
