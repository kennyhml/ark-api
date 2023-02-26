import os
from dataclasses import dataclass

from .._helpers import get_filepath


@dataclass
class Buff:
    name: str
    image: str


    def __post_init__(self) -> None:
        self.image = get_filepath(self.image)

        assert os.path.exists(self.image), f"Path not found: {self.image}"