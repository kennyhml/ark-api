import cv2  # type:ignore[import]
import pyautogui  # type: ignore[import]
import pydirectinput  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ..._ark import Ark
from ..._helpers import (await_event, find_center, find_closest_pixel,
                       get_center, get_filepath)
from ...exceptions import UnexpectedWheelError, WheelNotAccessibleError


class ActionWheel(Ark):
    """Represents the action wheel in Ark.

    Provides the ability to select certain tabs on the action wheel,
    check whether it is open, get the wheels text or find certain tabs.

    Wheels are useful because they help figure out if we just simply
    arent looking at a structure while trying to access it, or if lag
    is holding us back from opening it, because action wheels open regardless
    of lag or timer.

    Parameters
    ----------
    filepath :class:`str`:
        The filepath to an image of the action wheel
    """

    _WHEEL_NAME_AREA = (840, 425, 240, 230)
    _WHEEL_AREA = (543, 135, 867, 825)

    def __init__(self, name: str, filepath: str) -> None:
        super().__init__()
        self._name = name
        self._filepath = get_filepath(filepath)

    def __str__(self) -> str:
        return f"Action Wheel '{self._name}' of type '{type(self).__name__}' with filepath {self._filepath}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self._name}, filepath={self._filepath})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def filepath(self) -> str:
        return self._filepath

    def activate(self) -> None:
        """Brings up the action wheel. When the function ends, the 'E' key
        is still being held for further usage of the wheel. Remember to release
        it yourself when you need it gone.

        Raises
        ------
        `UnexpectedWheelError`
            If after 3 attempts a wheel is open but not the expected one

        `WheelNotAccessibleError`
            If no wheel could be opened after 5 attempts
        """
        attempts = 0
        while not self.is_open():
            pyautogui.keyDown(self.keybinds.use)
            if await_event(self.is_open, max_duration=2):
                break

            attempts += 1
            if attempts > 3:
                raise WheelNotAccessibleError(self._name)

            other_text = self.get_text()
            if len(other_text) > 5:
                raise UnexpectedWheelError(self._name, other_text)
                
            self.sleep(1)
            pyautogui.keyUp(self.keybinds.use)

    def deactivate(self) -> None:
        pyautogui.keyUp(self.keybinds.use)
        self.sleep(0.5)
        
    def select_action(self, position: tuple[int, int], click: bool = True) -> None:
        pydirectinput.moveTo(*position, duration=0.1)
        self.sleep(0.1)
        pydirectinput.moveTo(*position, duration=0.1)
        self.sleep(1)
        if click:
            self.click("left")

    def find_action(self, whitelist: str) -> tuple[int, int] | None:
        wheel = self.window.grab_screen(self._WHEEL_AREA)
        wheel_outer: cv2.Mat = self.window.denoise_text(
            wheel, (255, 255, 255), variance=14, dilate=False
        )

        height, _ = wheel_outer.shape

        boxes: str = tes.image_to_boxes(
            wheel_outer, config=f"-c tessedit_char_whitelist={whitelist} --psm 3"
        )
        points = []
        for box in boxes.splitlines():
            _, x, y, w, h, _ = box.split(" ")
            center = get_center(
                (
                    int(x),
                    height - int(y),
                    int(w) - int(x),
                    (height - int(h)) - (height - int(y)),
                )
            )
            points.append(
                (center[0] + self._WHEEL_AREA[0], center[1] + self._WHEEL_AREA[1])
            )

        if not points:
            return None

        com = find_center(points)
        return find_closest_pixel(points, com)

    def get_text(self) -> str:
        """Returns the text of the action wheel."""
        wheel_inner = self.window.grab_screen(self._WHEEL_NAME_AREA)
        wheel_inner_text = self.window.denoise_text(
            wheel_inner, (255, 209, 64), variance=7
        )
        raw: str = tes.image_to_string(
            wheel_inner_text,
            config="--psm 6 -l eng",
        )
        return raw.replace("\n", " ").replace("{", "(").replace("}", "}")

    def is_open(self) -> bool:
        """Returns whether the action wheel is currently open"""
        return (
            self.window.locate_template(
                self._filepath,
                region=self._WHEEL_NAME_AREA,
                confidence=0.7,
            )
            is not None
        )

    def in_access_range(self) -> bool:
        """Uses the action wheel to check if a structure or dinosaur is within
        access range to determine if we are unable to open it because of lag or
        if we are just not looking at it. Useful for time efficiency on crop plots.

        Returns `True` if the action wheel displays the structure / dinos name.
        """
        with pyautogui.hold("e"):
            self.sleep(1)
            return self.is_open()

    def export_data(self) -> None:
        self.activate()
        self.select_action((811, 470), click=True)
        self.sleep(1)
        self.select_action((850, 642), click=True)

        self.deactivate()