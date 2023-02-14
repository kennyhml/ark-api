from datetime import datetime
from typing import Literal, Optional

from .structure import Structure


class IndustrialForge(Structure):
    """Represents the Industrial Forge inventory in ark.

    Is able to be turned on and off.
    """

    BURNING_DURATIONS: dict[str, float | int] = {"wood": 2.8, "metal": 4.3, "oil": 0.7}

    def __init__(
        self,
        started_cooking: Optional[datetime] = None,
        burning_item: Literal["wood", "metal", "oil"] = "wood",
    ) -> None:

        super().__init__(
            "Industrial Forge",
            "assets/wheels/industrial_forge.png",
            max_slots="assets/interfaces/forge_full.png",
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