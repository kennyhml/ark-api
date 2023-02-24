from datetime import datetime
from typing import Literal, Optional, final

from ..._helpers import format_seconds
from .structure import Structure


@final
class IndustrialForge(Structure):
    """Represents the Industrial Forge in Ark.

    The industrial forge extends the abilities the `Structure` class, by adding
    methods to keep track of different types of items burning and checking on 
    how much longer is left on them to finish.

    Beware that, while you may consider charcoal, metal ingots or gasoline
    to be craftables of the `Industrial Forge`, they are not considered as such.
    It is defined as a toggleable, but items that are cooked in the forge are
    not technically crafted.

    Parameters
    ----------
    burning_item :class:`Literal["wood", "metal", "oil"]`:
        The item being cooked in the forge.

    started_cooking :class:`Optional[datetime]`:
        The time the forge started cooking, if not passed it will be assumed the
        forge never cooked.

    Properties
    ----------
    burning_item :class:`str`:
        The item being burnt, can be changed at runtime but with the same
        limitations as during the initialization.

    is_done_burning :class:`bool`:
        Whether the forge is done burning, taking into account the burning time
        of the item it is burning.
    """

    BURNING_DURATIONS: dict[str, float | int] = {"wood": 2.8, "metal": 4.3, "oil": 0.7}

    def __init__(
        self,
        burning_item: Literal["wood", "metal", "oil"] = "wood",
        started_cooking: Optional[datetime] = None,
    ) -> None:
        if burning_item not in ["wood", "metal", "oil"]:
            raise ValueError(
                f'Expected one of {["wood", "metal", "oil"]}, got "{burning_item}".'
            )
        super().__init__(
            name="Industrial Forge",
            action_wheel="assets/wheels/industrial_forge.png",
            capacity="assets/interfaces/forge_full.png",
            toggleable=True,
        )
        self.started_cooking = started_cooking
        self._burning_item = burning_item

    @property
    def burning_item(self) -> str:
        return self._burning_item

    @burning_item.setter
    def burning_item(self, item: Literal["wood", "metal", "oil"]) -> None:
        if not item in ["wood", "metal", "oil"]:
            raise ValueError(
                f'Cant burn {item}, expected one of {["wood", "metal", "oil"]}'
            )
        self._burning_item = item

    @property
    def is_done_burning(self) -> bool:
        if self.started_cooking is None:
            return True
        delta = datetime.now() - self.started_cooking
        return delta.total_seconds() > self.BURNING_DURATIONS[self.burning_item] * 3600

    @property
    def remaining_burn_time(self) -> str:
        if self.started_cooking is None:
            return "0"

        delta = datetime.now() - self.started_cooking
        duration = self.BURNING_DURATIONS[self.burning_item]
        
        remaining = (duration * 3600) - delta.total_seconds()
        return format_seconds(round(remaining))