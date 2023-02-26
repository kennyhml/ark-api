from typing import final

from ..spawn_screen import SpawnScreen
from .structure import Structure


@final
class Bed(Structure):

    def __init__(self, name: str) -> None:
        super().__init__(name, "assets/wheels/bed.png")
        self.interface = SpawnScreen()

    def spawn(self) -> None:
        self.interface.travel_to(self.name)


    def lay_down(self) -> None:
        self.action_wheel.activate()
        self.action_wheel.select_action((1130, 510), click=False)

    def get_up(self) -> None:
        self.press(self.keybinds.use)