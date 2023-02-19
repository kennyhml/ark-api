
from typing import final

from ..inventories import CropPlotInventory
from .structure import Structure


@final
class TekCropPlot(Structure):

    def __init__(self, name: str) -> None:
        super().__init__(name, "assets/wheels/tek_crop_plot.png")
        self.inventory = CropPlotInventory(name)