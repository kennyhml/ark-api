from typing import final

from ..inventories import CropPlotInventory
from .structure import Structure


@final
class TekCropPlot(Structure):
    def __init__(self, name: str) -> None:
        super().__init__(
            name, "assets/wheels/tek_crop_plot.png", inventory=CropPlotInventory(name)
        )

    def plant_is_visible(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/species.png",
                region=(0, 0, 1920, 1080),
                confidence=0.7,
            )
            is not None
        )
