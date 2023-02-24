import cv2 as cv  # type:ignore[import]
import numpy as np
import pyautogui  # type:ignore[import]

from ..._helpers import find_center, find_closest_pixel, get_center
from ...exceptions import ActionNotFoundError
from .wheel import ActionWheel


class StryderWheel(ActionWheel):
    def __init__(self) -> None:
        super().__init__("Stryder", "assets/wheels/stryder.png")

    def enter_dedi_transfer_tab(self) -> None:
        self.sleep(1)
        position = self.find_dedi_transfer_tab()
        if position is None:
            raise ActionNotFoundError("Dedi transfer")

        self.sleep(0.3)
        self.select_action(position)
        self.sleep(1)

    def enter_linked_dedi_tab(self) -> None:
        self.select_action((1145, 783))
        self.sleep(0.5)

    def transfer_to_nearby_dedis(self) -> None:
        self.select_action((960, 230))
        pyautogui.keyUp("e")

    def show_more(self) -> None:
        self.select_action((835, 263))

    def find_dedi_transfer_tab(self) -> tuple[int, int] | None:
        """Finds the dedi transfer tab by denoising for the orange text.

        Matching for the orange text template is not reliable because the text
        size changes depending on how many options are on the action wheel.

        Returns the coordinate of the transfer tab as a tuple, or None if not found.
        """
        img_arr = np.array(self.window.grab_screen(self._WHEEL_AREA))
        img = cv.cvtColor(img_arr, cv.COLOR_BGR2RGB)

        lower_bound = tuple(max(0, i - 15) for i in (255, 146, 39))
        upper_bound = tuple(min(255, i + 15) for i in (255, 146, 39))

        mask = cv.inRange(img, lower_bound, upper_bound)
        matches = cv.findNonZero(mask)
        if matches is None:
            return None

        matching_points = [
            (self._WHEEL_AREA[0] + x, self._WHEEL_AREA[1] + y)
            for x, y in np.concatenate(matches, axis=0)
        ]
        com = find_center(matching_points)
        return find_closest_pixel(matching_points, com)