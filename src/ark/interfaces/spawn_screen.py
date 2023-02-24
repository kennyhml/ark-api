import cv2 as cv  # type:ignore[import]
import numpy as np
import pyautogui  # type:ignore[import]

from .._ark import Ark
from .._helpers import await_event, get_center
from ..exceptions import BedNotAccessibleError, BedNotFoundError, PlayerDidntTravelError

from .. import config


class SpawnScreen(Ark):
    """Represents the spawn screen in Ark.

    Provides the ability to search for beds and detect them on the map,
    to then travel to them. If the bed icon itself cannot be found, the
    center of the red X will be assumed to be the correct location.
    """

    SEARCH_BAR = (306, 982)
    SPAWN_BUTTON = (731, 978)

    _BEDS_REGION = (160, 70, 1050, 880)
    _BED_NAME_AREA = (624, 967, 250, 25)

    def spawn(self) -> None:
        """Clicks the spawn button"""
        self.click_at(self.SPAWN_BUTTON)

    def search(self, name: str) -> None:
        """Searches for a bed"""
        self.click_at(self.SEARCH_BAR)
        with pyautogui.hold("ctrl"):
            pyautogui.press("a")

        pyautogui.typewrite(name.lower(), interval=0.001)
        self.sleep(0.3)

    def open(self) -> None:
        """Opens the bed menu. Times out after 30 unsuccessful
        attempts raising a `BedNotAccessibleError`"""
        attempt = 0
        while not self.is_open():
            attempt += 1
            self.press(self.keybinds.use)
            self.sleep(1)

            if attempt > 30:
                raise BedNotAccessibleError("Failed to access the bed!")

    def travel_to(self, bed_name: str) -> None:
        """Travels to a bed given it's name. If the spawn screen is not
        already open, it will be opened first.

        Parameters
        ----------
        name :class:`str`:
            The name of the bed to travel to
        """
        self.open()
        self.search(bed_name)

        position = self._find_bed() or self._find_x()
        if position is None:
            raise BedNotFoundError(f"Could not find '{bed_name}'!")

        self.click_at(position, delay=0.5)
        self.sleep(0.5)

        attempts = 0
        while not self._bed_is_selected():
            self.click_at(position, delay=0.5)
            if await_event(self._bed_is_selected, max_duration=1):
                break

            attempts += 1
            if attempts >= 2:
                raise BedNotFoundError(f"Could not select '{bed_name}'!")

            self.search(bed_name)
            position = self._find_bed() or self._find_x()

        if self._spawn_region_is_selected():
            raise BedNotFoundError(
                f"Could not find '{bed_name}'! Random spawn region was selected!"
            )

        self.spawn()
        if await_event(self._is_travelling, max_duration=15 * config.TIMER_FACTOR):
            self.sleep(2)
            return
        raise PlayerDidntTravelError(f"Failed to travel to bed '{bed_name}'!")

    def can_be_accessed(self) -> bool:
        """Returns whether the bed can be accessed, determined by the
        'Fast trave' text that appears when facing it."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/fast_travel.png",
                region=(0, 0, 1920, 1080),
                confidence=0.7,
            )
            is not None
        )

    def is_open(self) -> bool:
        """Returns whether the spawn screen is currently open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces//bed_filter.png",
                region=(140, 950, 150, 50),
                confidence=0.8,
            )
            is not None
        )

    def _find_bed(self) -> tuple[int, int] | None:
        """Finds the icon of a bed on the map, assuming the bed has already
        been searched."""
        img_arr = np.array(self.window.grab_screen(self._BEDS_REGION))
        img = cv.cvtColor(img_arr, cv.COLOR_BGR2RGB)

        lower_bound = tuple(max(0, i - 7) for i in (0, 255, 255))
        upper_bound = tuple(min(255, i + 7) for i in (0, 255, 255))

        mask = cv.inRange(img, lower_bound, upper_bound)
        contours, _ = cv.findContours(
            mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            return None

        contour = max(contours, key=cv.contourArea)
        if cv.contourArea(contour) < 10:
            return None

        point = get_center(cv.boundingRect(contour))
        return point[0] + 160, point[1] + 70

    def _find_x(self) -> tuple[int, int] | None:
        """Finds the red X on the map, assuming the bed has already
        been searched."""
        img_arr = np.array(self.window.grab_screen(self._BEDS_REGION))
        img = cv.cvtColor(img_arr, cv.COLOR_BGR2RGB)

        lower_bound = tuple(max(0, i - 7) for i in (255, 255, 255))
        upper_bound = tuple(min(255, i + 7) for i in (255, 255, 255))

        mask = cv.inRange(img, lower_bound, upper_bound)
        contours, _ = cv.findContours(
            mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            return None

        contour = max(contours, key=cv.contourArea)
        if cv.contourArea(contour) < 300:
            return None

        point = get_center(cv.boundingRect(contour))
        return point[0] + 160, point[1] + 70

    def _is_travelling(self) -> bool:
        """Check if we are currently travelling (whitescreen)"""
        return pyautogui.pixelMatchesColor(
            *self.window.convert_point(959, 493), (255, 255, 255), tolerance=10
        )

    def _bed_is_selected(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/bed_button.png",
                region=(587, 955, 35, 43),
                confidence=0.7,
            )
            is not None
        )

    def _spawn_region_is_selected(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/random_location.png",
                region=self._BED_NAME_AREA,
                confidence=0.85,
            )
            is not None
        )
