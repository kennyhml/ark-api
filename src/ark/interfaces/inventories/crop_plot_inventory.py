from typing import final

from .inventory import Inventory


@final
class CropPlotInventory(Inventory):

    _ITEM_REGION = (1243, 232, 561, 373)