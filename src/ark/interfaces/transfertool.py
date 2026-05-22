import time

from .._ark import Ark
from .._helpers import await_event, timedout
from ..exceptions import InterfaceError
import cv2 as cv


class TransferTool(Ark):

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
        return count > 50

    def use_preset(self, preset: int):
        positions = [
            (869, 785),
            (869, 812),
            (869, 842),
            (869, 864),
            (869, 892),
        ]

        start = time.time()
        last_click = time.time()

        while not self.is_presets_open():
            if timedout(start, 15):
                raise InterfaceError("Failed to open presets")

            if last_click is None or timedout(last_click, 3):
                self.click_at(943, 933)
                last_click = time.time()

        while self.is_presets_open():
            if timedout(start, 15):
                raise InterfaceError(f"Failed to use preset {preset}")

            if last_click is None or timedout(last_click, 3):
                self.click_at(positions[preset - 1])
                last_click = time.time()

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
