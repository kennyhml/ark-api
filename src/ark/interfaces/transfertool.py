import time

from .._ark import Ark
from .._helpers import await_event, timedout
from ..exceptions import InterfaceError
import cv2 as cv

import pyautogui as pg


class TransferTool(Ark):

    last_transfer = None

    def open(self) -> None:
        """Opens the escape menu."""
        start = time.time()

        while not self.is_open():
            self.click("left")
            if await_event(self.is_open, max_duration=3):
                return

            if timedout(start, 30):
                raise InterfaceError("Failed to open transfer tool!")

    def close(self) -> None:
        """Closes the escape menu."""
        start = time.time()

        while self.is_open():
            self.press("escape")
            if await_event(self.is_open, False, max_duration=3):
                return

            if timedout(start, 30):
                raise InterfaceError("Failed to close transertool!")
        Ark.last_interface_exit = time.time()

    def is_presets_open(self):
        roi = (1057, 749, 28, 150)
        img = self.window.grab_screen(roi)

        img = self.window.denoise_text(img, (101, 101, 101), variance=5, dilate=False)
        count = cv.countNonZero(img)
        return count > 10

    def use_preset(self, preset: int, times: int, max: int = None):
        positions = [
            (869, 785),
            (869, 812),
            (869, 842),
            (869, 864),
            (869, 892),
        ]

        start = time.time()
        last_click = None

        while not self.is_presets_open():
            if timedout(start, 15):
                raise InterfaceError("Failed to open presets")

            if last_click is None or timedout(last_click, 3):
                self.click_at(943, 933)
                last_click = time.time()
            self.sleep(0.3)

        last_click = None
        while self.is_presets_open():
            if timedout(start, 15):
                raise InterfaceError(f"Failed to use preset {preset}")

            if last_click is None or timedout(last_click, 3):
                self.click_at(positions[preset - 1])
                last_click = time.time()
            self.sleep(0.3)

        if max is not None:
            self.click_at(1477, 810)
            self.sleep(0.1)
            pg.typewrite(str(max))

        for _ in range(times):
            self.transfer()

    def transfer(self):
        while self.last_transfer is not None and time.time() - self.last_transfer < 1.2:
            self.sleep(0.1)

        self.click_at(580, 928)
        self.sleep(0.5)
        self.last_transfer = time.time()

    def is_open(self) -> bool:
        """Checks if the menu is open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/items_to_transfer.png",
                region=(836, 121, 247, 44),
                confidence=0.8,
            )
            is not None
        )

    def no_items_transferred(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/0_items_transferred.png",
                region=(872, 820, 83, 73),
                confidence=0.85,
            )
            is not None
        )
