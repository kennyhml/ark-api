import time
from pathlib import Path
from typing import Optional

import pyautogui as pg  # type: ignore[import]
import pydirectinput  # type: ignore[import]
from pynput.mouse import Button, Controller  # type: ignore[import]

from ._helpers import state_checker
from .settings import InputSettings, UserSettings
from .window import ArkWindow

pg.FAILSAFE = False
pydirectinput.FAILSAFE = False


class Ark:
    """Base parent class for all classes representing objects in ark
    Provides access to the games window, mouse and keypress simulation,
    and program state checking.
    """

    PKG_DIR = str(Path(__file__).parent)
    window: ArkWindow = None  # type:ignore[assignment]
    keybinds: InputSettings = None  # type:ignore[assignment]
    settings: UserSettings = None  # type:ignore[assignment]
    mouse = Controller()

    def __init__(self, reinit: bool = False) -> None:
        if Ark.window is None or reinit:
            Ark.window = ArkWindow()

        if Ark.keybinds is None or reinit:
            Ark.keybinds = InputSettings.load()

        if Ark.settings is None or reinit:
            Ark.settings = UserSettings.load()

    @state_checker
    def sleep(self, duration: int | float) -> None:
        """Sleeps for a given duration"""
        time.sleep(duration)

    @state_checker
    def move_to(
        self,
        x: Optional[int | tuple] = None,
        y: Optional[int | tuple] = None,
        convert: bool = True,
    ) -> None:
        """Moves to the given position, scales passed coordinates by default.
        Parameters
        -----------
        x, y: :class:`int` | `tuple`
            The coordinates to move to, normalized

        convert: :class:`bool`
            Convert the coordinate to the current resolution

        ignore_limits: :class:`bool`:
            Whether to ignore the max x and y axis thats allowed to move to
        """
        pos: tuple[int, int] = pg._normalizeXYArgs(x, y)
        x, y = pos

        # we may not need to convert if the point comes from a template match
        if convert:
            x, y = self.window.convert_point(x, y)
        pg.moveTo(x, y)

    @state_checker
    def press(self, key: str) -> None:
        """Presses the given key"""
        self.window.set_foreground()
        if key not in ["thumbmousebutton2", "thumbmousebutton"]:
            pg.press(key)
            return

        # use pynputs Controller to emulate side mouse button presses
        self.mouse.click(Button.x1 if key != "thumbmousebutton2" else Button.x2)

    @state_checker
    def mouse_scroll(self, amount: int) -> None:
        self.mouse.scroll(0, amount)

    @state_checker
    def click(self, button: str) -> None:
        """Presses the given button"""
        pg.click(button=button)

    @state_checker
    def click_with_delay(self, delay: float | int = 0.2) -> None:
        """Left clicks with a given delay."""
        self.sleep(delay)
        pg.click()
        self.sleep(delay)

    def click_at(
        self, x=None, y=None, button: str = "left", delay: float = 0.1, clicks: int = 1
    ):
        """Moves to a given location and clicks with the mouse.
        Parameters:
        ----------
        pos: :class:`tuple`
            The (x,y) coordinates of the point
        button: :class:`str`
            The button to press
        """
        self.window.set_foreground()
        x, y = pg._normalizeXYArgs(x, y)
        self.move_to(x, y)
        self.sleep(delay)
        pg.click(button=button, clicks=clicks)
        self.sleep(0.1)
