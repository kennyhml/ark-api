import cv2 as cv  # type: ignore[import]
import numpy as np
import pydirectinput as input  # type: ignore[import]

from .dinosaur import Dinosaur


class Stryder(Dinosaur):
    """Represents a stryder in ark, used for resource logistics."""

    def __init__(self) -> None:
        super().__init__("Tek Stryder", "assets/wheels/stryder.png")

    def find_dedi_transfer_tab(self) -> tuple | None:
        """Finds the dedi transfer tab by denoising for the orange text.

        Matching for the orange text template is not reliable because the text
        size changes depending on how many options are on the action wheel.

        Returns the coordinate of the transfer tab as a tuple, or None if not found.
        """
        # grab action wheel region, denoise for orange text
        img = self.window.grab_screen((470, 80, 980, 900))
        mask = self.window.denoise_text(img, (39, 146, 255), 15)

        # get the first orange matching pixel
        matches = cv.findNonZero(mask)
        if matches is None:
            return None

        return [(470 + x, 80 + y) for x, y in np.concatenate(matches, axis=0)][0]

    def open_dedi_transfer_wheel(self) -> None:
        """Opens the dedi transfer action wheel."""
        # find position of the wheel option
        pos = self.find_dedi_transfer_tab()
        if not pos:
            raise LookupError("Failed to find dedi transfer action!")

        # enter the option
        self.sleep(0.5)
        input.moveTo(*pos, duration=0.1)
        self.sleep(0.1)
        input.moveTo(*pos, duration=0.1)
        self.sleep(1)
        self.click("left")
        self.sleep(1)

    def click_sort_to_nearby_dedis(self) -> None:
        """Clicks the 'sort to nearby dedis' in the open action wheel."""
        input.keyDown("e")
        input.moveTo(960, 230, duration=0.1)
        self.sleep(0.1)
        input.moveTo(960, 230, duration=0.1)
        self.sleep(1)
        self.click("left")
        input.keyUp("e")

    def sort_items_to_nearby_dedis(self) -> None:
        """Uses the stryders action wheel to sort all the items in the stryders
        inventory to nearby dedis."""
        self.action_wheel.activate()
        self.sleep(2)
        self.open_dedi_transfer_wheel()
        self.click_sort_to_nearby_dedis()