from .structure import Structure


class ChemistryBench(Structure):
    """Represents the chem bench in ark.
    Is able to be turned on and off.
    """

    def __init__(self) -> None:
        super().__init__("Chemistry Bench", "chem_bench")