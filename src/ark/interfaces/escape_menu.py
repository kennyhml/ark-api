import time

from .._ark import Ark
from .._helpers import await_event, timedout
from ..exceptions import InterfaceError


class EscapeMenu(Ark):
    """Represents the Escape Menu in Ark.

    Provides the ability to open or close it, which is useful for clearing the screen
    i.e close unwanted interfaces.
    """

    _RESUME_REGION = (750, 215, 425, 200)

    def open(self) -> None:
        """Opens the escape menu."""
        start = time.time()

        while not self.is_open():
            self.press("escape")
            if await_event(self.is_open, max_duration=3):
                return

            if timedout(start, 30):
                raise InterfaceError("Failed to open escape menu!")

    def close(self) -> None:
        """Closes the escape menu."""
        start = time.time()

        while self.is_open():
            self.press("escape")
            if await_event(self.is_open, False, max_duration=3):
                return

            if timedout(start, 30):
                raise InterfaceError("Failed to close escape menu!")

    def is_open(self) -> bool:
        """Checks if the menu is open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/resume.png",
                region=self._RESUME_REGION,
                confidence=0.8,
            )
            is not None
        )
