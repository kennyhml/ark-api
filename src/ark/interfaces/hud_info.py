import pyautogui  # type:ignore[import]
from pytesseract import pytesseract as tes  # type:ignore[import]

from .._ark import Ark
from .._helpers import await_event
from ..exceptions import InterfaceError, TimerNotVisibleError


class HUDInfo(Ark):
    """Represents the extended HUD Info in Ark.
    
    Provides the ability to get the current timer assuming tek
    gauntlets are equipped.
    """

    _DAY_REGION = (0, 10, 214, 95)
    _TIMER_WORD_REGION = (90, 130, 78, 28)
    _TIMER_REGION = (164, 127, 69, 30)

    def open(self) -> None:
        """Opens the HUD info, key stays in a held state!"""
        attempts = 0
        while not self.is_open():
            pyautogui.keyDown(self.keybinds.hud_info)

            if await_event(self.is_open, max_duration=3):
                return
            pyautogui.keyUp(self.keybinds.hud_info)
            self.sleep(0.3)
            attempts += 1
            if attempts > 4:
                raise InterfaceError("Failed to open HUD!")

    def is_open(self) -> bool:
        """Returns whether the HUD info interface is open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/day.png",
                region=self._DAY_REGION,
                confidence=0.75
            )
            is not None
        )

    def can_get_timer(self) -> bool:
        """Returns whether the timer is visible"""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/timer.png",
                region=self._TIMER_WORD_REGION,
                confidence=0.7
            )
            is not None
        )

    def get_timer(self) -> int | None:
        """Returns the timer as total seconds, or `None` if not determined.
        
        If the timer is not visible, it will raise a `TimerNotVisibleError`.
        """
        self.open()
        if not self.can_get_timer():
            raise TimerNotVisibleError
        return self._fetch_timer()

    def _fetch_timer(self) -> int | None:
        """Fetches the timer by denoising the timer region and then OCR'ing
        the text."""
        img = self.window.grab_screen(self._TIMER_REGION)
        img = self.window.denoise_text(img, (63, 179, 255), variance=15)

        raw: str = tes.image_to_string(
            img, config=f"-c tessedit_char_whitelist=0123456789liIxObL: --psm 7 -l eng"
        ).strip()

        if ":" not in raw or len(raw) < 4:
            return None
            
        minutes, seconds = raw.split(":")
        return (int(minutes) * 60) + int(seconds)
