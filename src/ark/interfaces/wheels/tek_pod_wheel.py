import cv2 as cv  # type:ignore[import]
import numpy as np
import pyautogui  # type:ignore[import]

from ..._tools import find_center, find_closest_pixel, get_center
from ...exceptions import ActionNotFoundError
from .wheel import ActionWheel


class TekPodWheel(ActionWheel):
    def __init__(self) -> None:
        super().__init__("Tek Sleeping Pod", "assets/wheels/pod.png")

    def lay_on(self) -> None:
        self.select_action((1166, 495), click=False)
        pyautogui.keyUp(self.keybinds.use)