from typing import Optional

from .._ark import Ark
from ..interfaces import Inventory


class Structure(Ark):
    """Represents a structure in ark.

    TODO:
    Give it more meaningful methods and attributes, for example if
    items can be crafted in it, what items can be crafted in it,
    if it can be turned on and off, how long it would be crafting / cooking
    for...
    """

    def __init__(
        self, name: str, action_wheel: str, max_slots: Optional[str] = None
    ) -> None:
        super().__init__()
        self.inventory = Inventory(name, action_wheel, max_slots)
