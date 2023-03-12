from typing import Generator

import cv2 as cv  # type: ignore[import]
import numpy as np
from mss.screenshot import ScreenShot  # type: ignore[import]
from PIL import Image  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ..._ark import Ark
from ...exceptions import LogsNotOpenedError
from .._button import Button
from ._config import (CONTENTS_MAPPING, DAYTIME_MAPPING, DENOISE_MAPPING,
                      EVENT_MAPPING, INGORED_TERMS)
from ._message import TribeLogMessage


class TribeLog(Ark):
    """Represents the ark tribe log. Stores all previous logs as a
    list of `TribeLogMessages`.

    Attributes:
    --------------------
    tribe_log :class:`list`:
        A list containing the past 30 tribe log events as `TribeLogMessages`
    """

    LOG_REGION = 1340, 180, 460, 820

    _ONLINE_AXIS = (1132, 315, 111, 720)

    _TOGGLE_ONLINE = Button(
        (1063, 125), (1035, 97, 52, 52), "toggle_online_members.png"
    )

    def __init__(self) -> None:
        super().__init__()
        self._tribe_log: list[TribeLogMessage] = []
        self._online_members: int | None = None

    def __repr__(self) -> str:
        """A representative string of the log message"""
        return "".join(f"{log_message}\n" for log_message in self._tribe_log)
    
    def __iter__(self) -> Generator[TribeLogMessage, None, None]:
        for message in self._tribe_log:
            yield message

    @property
    def online_members(self) -> str:
        if self._online_members is None:
            return "?"
        if self._online_members >= 12:
            return "12+"
        return str(self._online_members)

    def toggle_online_members(self) -> None:
        assert self._TOGGLE_ONLINE.template and self._TOGGLE_ONLINE.region

        if self.window.locate_template(
            self._TOGGLE_ONLINE.template, self._TOGGLE_ONLINE.region, confidence=0.8
        ):
            return
        self.click_at(self._TOGGLE_ONLINE.location)

    def find_tribelog_events(self, img: ScreenShot) -> list[TribeLogMessage]:
        """Runs a scan on the tribelog snapshot to find all 'Day' occurrences, then
        extracts the message and checks for contents. Adds new messages to the tribelog
        and posts them as alert if they are relevant.
        """
        # sort days from top to bottom by y-coordinate so we can get the message frame
        image_array = np.array(img)
        image_rgb = cv.cvtColor(image_array, cv.COLOR_BGR2RGB)
        image = Image.fromarray(image_rgb)

        day_points = self.get_day_occurrences(image)
        days_in_order = sorted([day for day in day_points], key=lambda t: t[1])

        messages: list[TribeLogMessage] = []
        for i, box in enumerate(days_in_order, start=1):
            try:
                # get relevant regions
                day_region = self.grab_day_region(box)
                message_region = self.grab_message_region(box, days_in_order[i])
            except IndexError:
                break
            try:
                day = self.get_daytime(image.crop(day_region))
                if not day:
                    continue
                
                content = self.get_message_contents(image.crop(message_region))
                if not content:
                    continue
                
                if self.day_is_known(day) or self.content_is_irrelevant(content[1]):
                    continue

            except Exception:
                continue

            # new message with relevant contents, create message object and add it
            # to the new messages
            message = TribeLogMessage(day, *content)
            messages.append(message)

        post = len(self._tribe_log) != 0
        self._tribe_log += reversed(messages)
        self.delete_old_logs()
        return list(reversed(messages)) if post else []

    def grab_current_events(self) -> ScreenShot:
        return self.window.grab_screen(self.LOG_REGION)

    def get_online_members(self) -> None:
        self.toggle_online_members()
        online = len(
            self.window.locate_all_template(
                f"{self.PKG_DIR}/assets/interfaces/online.png",
                region=self._ONLINE_AXIS,
                confidence=0.7,
                grayscale=True,
            )
        )
        self._online_members = online

    def is_open(self) -> bool:
        """Checks if the tribelog is open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/tribe_log.png",
                region=(1300, 70, 230, 85),
                confidence=0.8,
            )
            is not None
        )

    def open(self) -> None:
        """Opens the tribe log. Tries up to 20 times and raises a
        `LogsNotOpenedError` if unsuccessful.
        """
        c = 0
        while not self.is_open():
            self.press(self.keybinds.logs)
            if self.await_open():
                break
            c += 1
            if c > 20:
                raise LogsNotOpenedError("Failed to open logs!")

        # litle buffer in case timer pops or server lags
        self.sleep(2)

    def close(self) -> None:
        """Closes the tribelogs."""
        while self.is_open():
            self.press("esc")
            if self.await_closed():
                return

    def await_open(self) -> bool:
        """Awaits for the logs to be open to be time efficient.

        to do: write a parent `await` function that does this stuff
        """
        c = 0
        while not self.is_open():
            self.sleep(0.1)
            c += 1
            if c > 10:
                return False
        return True

    def await_closed(self) -> bool:
        """Awaits for the logs to be open to be time efficient."""
        c = 0
        while self.is_open():
            self.sleep(0.1)
            c += 1
            if c > 50:
                return False
        return True

    def grab_day_region(self, box) -> tuple[int, int, int, int]:
        """Grab the day regions located in the top left of the image.
        Adds a little padding on the top, left corner.

        NOTE:
        Int typecasing is neccessary because `box` is of type np.int
        which is not compatible with the cropping.
        """
        return (
            int(box[0] - 5),
            int(box[1] - 5),
            box[0] + 170,
            box[1] + 15,
        )

    def grab_message_region(self, box, next_box) -> tuple[int, int, int, int]:
        """Grabs the region of the message to read using the following message
        as delimiter for the y-axis.

        NOTE:
        Int typecasing is neccessary because `box` is of type np.int
        which is not compatible with the cropping.
        """
        return (
            int(box[0] - 5),
            int(box[1] - 5),
            440,
            int(next_box[1] - 2),
        )

    def content_is_irrelevant(self, content: str) -> bool:
        """Checks if the given content is relevant to be posted.

        Parameters:
        ------------
        content :class:`str`:
            The content to check

        Returns:
        ------------
        Whether an ignored term was found in the contents
        """
        return any(term in content for term in INGORED_TERMS)

    def get_day_occurrences(self, img: Image.Image) -> list[tuple]:
        """Retuns a list of all days, each day being a
        tuple containing top, left, widht and height"""

        img = img.crop(box=(0, 0, 50, img.height))

        return self.window.locate_all_in_image(
            f"{self.PKG_DIR}/assets/tribelog/tribelog_day.png", img, confidence=0.8
        )

    def get_daytime(self, image: str | Image.Image | ScreenShot) -> str | None:
        """Gets the daytime in the given image. The image is denoised and common
        mistakes are filtered out, then the day is validated.

        Parameters:
        -----------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to get the daytime of

        Returns:
        -----------
        daytime :class:`str` | `None`:
            The daytime to be seen in the image or `None` if it is invalid / undetermined.
        """
        # prepare the image, denoising upscaling dilating etc...
        prepared = self.window.denoise_text(
            image, denoise_rgb=(180, 180, 180), variance=18, upscale=True, upscale_by=2
        )

        # get tesseract result, whitelisting seems to not be working too well.
        raw_day_string = tes.image_to_string(prepared, config="--psm 6 -l eng")

        # replace the potentially mistaken characters
        for c in DAYTIME_MAPPING:
            raw_day_string = raw_day_string.replace(c, DAYTIME_MAPPING[c])
        day_string = raw_day_string

        try:
            # split the day into the parts we care about
            day = day_string.split(" ")[1].replace(",", "")
            hour, min, sec = (day_string.split(" ")[2].split(":")[i] for i in range(3))

            # check that all values make logical sense
            if any((len(day) > 5, int(hour) > 24, int(min) > 60, int(sec) > 60)):
                return None

        except Exception as e:
            return None

        return day_string.strip()

    def get_message_contents(
        self, image: str | Image.Image | ScreenShot
    ) -> tuple[str, str] | None:
        """Gets the contents of the given tribelog message image.

        Parameters:
        ------------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to get the contents of

        Returns:
        ------------
        contents :class:`tuple`:
            The contents of the image as a tuple of strings containing the action
            such as "Something destroyed!" and the actual contents.
        """
        # grab the rgb we need to use to denoise the image properly
        # if None there is no meaningful contents in the image
        denoise_rgb = self.get_denoise_rgb(image)
        if not denoise_rgb:
            return None

        # prepare the image for tesseract, the purple RGB needs higher variance
        # than the others. Dilating seems to give accurate results in this case.
        prepared_img = self.window.denoise_text(
            image,
            denoise_rgb,
            30 if not denoise_rgb == (208, 3, 211) else 50,
            upscale=True,
            upscale_by=2,
        )

        # get the raw tesseract result, assuming a uniform block of text.
        raw_res: str = tes.image_to_string(prepared_img, config="--psm 6 -l eng")

        # replace the common known mistakes that tend to happen
        for c in CONTENTS_MAPPING:
            raw_res = raw_res.replace(c, CONTENTS_MAPPING[c])
        filtered_res = raw_res.rstrip()

        if EVENT_MAPPING[denoise_rgb] == "Tek Sensor triggered!":
            sensor_event = self.get_sensor_event(image)
            filtered_res = f"'{filtered_res.rstrip()}' triggered by {sensor_event}!"
            event = "Tek Sensor triggered!"

        if "killed" in filtered_res:
            event = "Something killed!"
        elif "destroyed" in filtered_res:
            event = "Something destroyed!"

        return event, filtered_res

    def get_denoise_rgb(
        self, image: str | Image.Image | ScreenShot
    ) -> tuple[int, int, int] | None:
        """Gets the RGB to denoise for in the given image.

        Parameters:
        ------------
        image :class:`str`| `Image.Image` | `ScreenShot`:
            The image to be denoised

        Returns:
        -----------
        denoise_rgb :class:`tuple`:
            The rgb  value to denoise in the image for a good result
        """
        # absolute pain, need to convert to BGR and back for some reason
        if isinstance(image, ScreenShot):
            image = np.array(image)
            image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        elif isinstance(image, str):
            image = cv.imread(image, 1)

        else:
            # convert PIL image to np array for template matching
            image = np.array(image)
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        try:
            # filter out auto-decay
            if self.window.locate_in_image(
                f"{self.PKG_DIR}/assets/tribelog/tribelog_auto_decay.png",
                image,
                confidence=0.8,
            ):
                return None

            # find the RGB we need to denoise
            for rgb in DENOISE_MAPPING:
                template = DENOISE_MAPPING[rgb]

                # only 1 template to match
                if not isinstance(template, list):
                    if (
                        self.window.locate_in_image(template, image, confidence=0.8)
                        is not None
                    ):
                        return rgb
                    continue

                # multiple templates to match, check if any match
                if any(
                    self.window.locate_in_image(template, image, confidence=0.8)
                    is not None
                    for template in DENOISE_MAPPING[rgb]
                ):
                    return rgb
            return None

        except Exception as e:
            print(f"Something went wrong!\n{e}")
            return None

    def get_sensor_event(self, image: Image.Image | str) -> str:
        """Matches for different terms that could have triggered a tek sensor,
        returns the corresponding term.

        Parameters:
        ------------
        image :class:`Any image type compatible with pyautogui.locate`

        Returns:
        ------------
        A string representing the tek sensor event in the passed image.
        """
        if self.window.locate_in_image(
            f"{self.PKG_DIR}/assets/tribelog/tribelog_enemy_survivor.png",
            image,
            confidence=0.75,
        ):
            return "an enemy survivor"

        if self.window.locate_in_image(
            f"{self.PKG_DIR}/assets/tribelog/tribelog_enemy_dino.png",
            image,
            confidence=0.75,
        ):
            return "an enemy dinosaur"
        # not determined
        return "something (friendly or undetermined)"

    def day_is_known(self, day: str) -> bool:
        """Checks if the given day has already been recognized.

        Parameters:
        ------------
        day :class:`str`:
            The day to check for

        Returns:
        ------------
        `True` if the day is already in the database else `False`
        """
        # initial log save, no days known yet
        if not self._tribe_log:
            return False

        # typecast both days to integer to use integer operations
        day_int = int(day.split(" ")[1].replace(",", ""))
        most_recent_day = int(self._tribe_log[-1].day.split(" ")[1].replace(",", ""))

        # check if the day to check is smaller or too high compared to our most recent day
        if day_int < most_recent_day or day_int > most_recent_day + 20:
            return True

        # check if any of the saved messages already contain the day
        for message in self._tribe_log:
            if day.strip() == message.day.strip():
                return True
        return False

    def delete_old_logs(self) -> None:
        """Deletes all but the past 30 messages in the tribelogs."""
        if len(self._tribe_log) < 30:
            return

        self._tribe_log = self._tribe_log[-30:]
