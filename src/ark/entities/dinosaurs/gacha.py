
from .dinosaur import Dinosaur


class Gacha(Dinosaur):
    def __init__(self, name: str) -> None:
        super().__init__(name, "assets/wheels/gacha.png")