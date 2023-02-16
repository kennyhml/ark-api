from typing import final

from ...items import GUNPOWDER, SPARKPOWDER
from ..spawn_screen import SpawnScreen
from .structure import Structure


@final
class Bed(Structure):

    def __init__(self, name: str) -> None:
        super().__init__(name, "assets/wheels/bed.png")
        self.interface = SpawnScreen()

    def spawn(self) -> None:
        self.interface.travel_to(self.name)