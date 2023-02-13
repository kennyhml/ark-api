
from .structure import Structure


class IndustrialForge(Structure):
    """Represents the Industrial Forge inventory in ark.

    Is able to be turned on and off.
    """

    def __init__(self) -> None:
        super().__init__("Industrial Forge", "indi_forge")