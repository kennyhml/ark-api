import pyautogui as pg  # type: ignore[import]

from .._ark import Ark
from .._helpers import await_event


class Console(Ark):
    """Represents the Console in Ark.
    
    Provides the ability to enter commands such as t.maxfps, gamma...
    """

    COMMANDS = ["t.maxfps", "gamma", "disconnect", "reconnect", "exit"]

    def is_open(self) -> bool:
        """Returns whether the console is open by matching the black par"""
        return pg.pixelMatchesColor(
            *self.window.convert_point(976, 1071), (0, 0, 0), tolerance=3
        )

    def open(self):
        """Opens the console, times out after 10 seconds"""
        attempts = 0
        while not self.is_open():
            self.press(self.keybinds.console)
            if await_event(self.is_open, max_duration=3):
                return
            attempts += 1
            if attempts > 3:
                raise TimeoutError("Failed to open the console")

    def run(self, command: str) -> None:
        """Executes a given command in the console."""
        self.open()

        pg.typewrite(command, interval=0.001)
        self.sleep(0.5)
        self.press("enter") 

    def set_fps(self, fps: int | str = 10):
        """Sets the fps to a given value"""
        self.open()

        pg.typewrite(f"t.maxfps {fps}", interval=0.001)
        self.sleep(0.5)
        self.press("enter")

    def set_gamma(self, gamma: int | str = 5):
        """Sets gamma to a given value"""
        self.open()

        pg.typewrite(f"gamma {gamma}", interval=0.001)
        self.sleep(0.5)
        self.press("enter")

    def run_required_commands(self):
        """Sets up max fps and gamma with default parameters"""
        self.set_fps()
        self.set_gamma()
