from typing import final

from ...items import GUNPOWDER, SPARKPOWDER
from .structure import Structure


@final
class ChemistryBench(Structure):
    """Represents the chem bench in ark.
    Is able to be turned on and off.
    """

    def __init__(self) -> None:
        super().__init__(
            "Chemistry Bench",
            "assets/wheels/chemistry_bench.png",
            craftables=[SPARKPOWDER, GUNPOWDER],
            toggleable=True
        )




