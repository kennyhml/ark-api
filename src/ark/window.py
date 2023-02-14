"""
Ark API module handling the ark window.

All further ark classes should derive from `ArkWindow` as it provides the
methods neccessary to deal with alot of screen related stuff as well as
converting points, regions and even images to the resolution the game is running
in.

Note that the ark window class expects points and templates to be taken on 1920x1080
resolution.
"""
from typing import Literal, overload
import cv2 as cv  # type: ignore[import]
import numpy as np
import PIL  # type: ignore[import]
import pyautogui as pg  # type: ignore[import]
import pygetwindow  # type: ignore[import]
from mss import mss, tools  # type: ignore[import]
from PIL import Image, ImageOps
from pytesseract import pytesseract as tes  # type: ignore[import]
from screeninfo import get_monitors  # type: ignore[import]

from ._tools import get_center

# set tesseract path
tes.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ArkWindow:
    """ARK window handle

    Contains the boundaries of the game and the monitor it is running on.
    Scales points, regions and images depending on the games resolution.

    Contains methods to grab screenshots, match templates and check if the game
    is running. If no ark window could be grabbed, it assumes a regular 1920x1080
    ark window running on a 1920x1080 monitor.

    Attributes:
    ----------
    window :class:`dict`:
        A dictionary containing the games boundaries

    monitor :class:`dict`:
        A dictionary containing the boundaries of the monitor the game is running on

    fullscreen :class:`bool`:
        Whether the game is running in fullscreen or not.
    """

    _CORRECT_Y = 31
    _CORRECT_X = 8

    def __init__(self) -> None:
        self._boundaries = self.get_boundaries()
        self._monitor = self.get_monitor()
        self._fullscreen = self.check_fullscreen()
        print(self)

    def __str__(self) -> str:
        return (
            f"Lost Ark window: {self._boundaries}\n"
            f"Lost Ark Monitor: {self._monitor}\n"
            f"Lost Ark fullscreen: {self._fullscreen}"
        )

    @property
    def handle(self) -> int:
        return self._handle._hWnd

    @property
    def boundaries(self) -> dict:
        return self._boundaries

    @property
    def monitor(self) -> dict:
        return self._monitor

    @property
    def fullscreen(self) -> bool:
        return self._fullscreen

    @property
    def center(self) -> tuple[int, int]:
        return (
            self._boundaries["left"] + (self._boundaries["width"] // 2),
            self._boundaries["top"] + (self._boundaries["height"] // 2),
        )

    def grab_screen(
        self, region: tuple[int, int, int, int], path: str = "", convert: bool = True
    ) -> str:
        """Grabs a screenshot of the given region using mss and saves it
        at the specified path.

        Parameters:
        ---------
        Region :class:`tuple`:
            The region of the area to screenshot as (x, y, w, h)

        Path :class:`str`:
            The path to save the image at

        convert :class:`bool`:
            Decides if the given region will be converted or not

        Returns:
        ---------
        The specified path, to improve usage possibilites
        """
        with mss() as sct:
            # set region
            if convert:
                region = self.convert_region(region)
            x, y, w, h = region

            region_dict = {"left": x, "top": y, "width": w, "height": h}

            # grab img
            img = sct.grab(region_dict)

            if path:
                # Save to the picture file
                tools.to_png(img.rgb, img.size, output=path)
                return path
            return img

    def get_boundaries(self) -> dict:
        """Grab the ark window using pygetwindow and create the boundaries.
        If it fails to grab a window it will assume a 1920x1080 window.
        """
        try:
            windows = pygetwindow.getWindowsWithTitle("ARK: Survival Evolved")
            self._handle: pygetwindow.Win32Window = windows[0]
            print(f"Ark window handle: {self._handle._hWnd}")

            # create a window dict for mss
            return {
                "left": self._handle.left + self._CORRECT_X if self._handle.left else 0,
                "top": self._handle.top + self._CORRECT_Y if self._handle.top else 0,
                "width": self._handle.width,
                "height": self._handle.height,
            }
        except Exception as e:
            print(
                f"Could not grab the ark boundaries!\n{e}\n\n"
                "Assuming a 1920x1080 windowed fullscreen game."
            )
            return {"left": 0, "top": 0, "width": 1920, "height": 1080}

    def get_monitor(self) -> dict:
        """Gets the monitor boundaries of the monitor ark is running on
        and makes sure its the primary monitor

        Returns:
        ---------
        The boundaries of the monitor ARK is running on
        """
        center = self.center

        for m in get_monitors():
            # check x spacing
            if not (m.x < center[0] and center[0] < m.x + m.width):
                continue

            # check y spacing
            if not (m.y < center[1] and center[1] < m.y + m.height):
                continue

            # create a dict of the monitor
            return {
                "left": m.x,
                "top": m.y,
                "width": m.width,
                "height": m.height,
            }

        print(
            "Could not find then monitor ARK is running on!\n"
            "Assuming a 1920x1080 monitor."
        )
        return self._boundaries

    def check_fullscreen(self) -> bool:
        """Checks if ARK is running in fullscreen by checking if the monitor
        dict matches the ARK boundaries.
        """
        return all(
            [
                self._boundaries[boundary] == self._monitor[boundary]
                for boundary in ["left", "top", "width", "height"]
            ]
        )

    def need_boundary_scaling(self):
        """Checks if we need to scale width and height on regions or images"""
        return False

    def update_boundaries(self):
        """Re-initializes the class to update the window"""
        self._boundaries = self.get_boundaries()
        self._monitor = self.get_monitor()
        self._fullscreen = self.check_fullscreen()

    def convert_width(self, width) -> int:
        """Converts the width if it needs to be scaled."""
        if not self.need_boundary_scaling():
            return width

        return self.convert_point(width, 0)[0]

    def convert_height(self, height) -> int:
        """Converts the width if it needs to be scaled."""
        if not self.need_boundary_scaling():
            return height

        return self.convert_point(0, height)[1]

    def convert_point(self, x=None, y=None):
        """Converts the given point to the corresponding point on the ARK window"""
        # Normalize the position using pyautogui
        x, y = pg._normalizeXYArgs(x, y)

        # check for fullscreen converting
        if self._fullscreen:
            return (
                int((x / 1920) * self.monitor["width"]),
                int((y / 1080) * self.monitor["height"]),
            )

        return (
            self.monitor["left"] + x + self._boundaries["left"],
            self.monitor["top"] + y + self._boundaries["top"],
        )

    def convert_region(self, region: tuple):
        """Converts the given region to the corresponding region on the ARK window"""
        x, y, w, h = region

        # check if we can apply native scaling
        if not self.need_boundary_scaling():
            return (*self.convert_point(x, y), w, h)

        return (*self.convert_point(x, y), *self.convert_point(w, h))

    def convert_image(self, image: str) -> Image.Image | str:
        """Converts the given image to an upscaled image of ARKs resolution.

        Parameters:
        ----------
        image: :class:`str`:
            The path of the image to convert

        Returns:
        ----------
        A PIL `Image.Image` or the path if no converting was needed.
        """
        # check if we need to scale at all
        if not self.need_boundary_scaling():
            return image

        # open the image in PIL and use ImageOps to upscale it (maintains aspect ratio)
        raw_image = Image.open(image)
        new_width = self.convert_point(raw_image.width, raw_image.height)
        return ImageOps.contain(raw_image, new_width, PIL.Image.Resampling.LANCZOS)

    def locate_in_image(
        self, template: str, image, confidence: float, grayscale: bool = False
    ):
        """Finds the location of the given image in the given template."""
        return pg.locate(template, image, confidence=confidence, grayscale=grayscale)

    def locate_all_in_image(
        self, template: str, image, confidence: float, grayscale: bool = False
    ):
        """Finds all locations of the given image in the given template"""
        return self.filter_points(
            set(
                pg.locateAll(
                    template,
                    image,
                    confidence=confidence,
                    grayscale=grayscale,
                )
            ),
            min_dist=15,
        )

    @overload
    def locate_template(
        self,
        template: str,
        region: tuple[int, int, int, int],
        confidence: float,
        *,
        grayscale: bool = False,
        convert: bool = True,
        center: Literal[True],
    ) -> tuple[int, int] | None:
        ...

    @overload
    def locate_template(
        self,
        template: str,
        region: tuple[int, int, int, int],
        confidence: float,
        *,
        grayscale: bool = False,
        convert: bool = True,
        center: Literal[False] = False,
    ) -> tuple[int, int, int, int] | None:
        ...
        
    def locate_template(
        self,
        template: str,
        region: tuple[int, int, int, int],
        confidence: float,
        *,
        grayscale: bool = False,
        convert: bool = True,
        center: bool = False,
    ) -> tuple[int, int, int, int] | tuple[int, int] | None:
        """Returns the locations of an image on the screen.

        Parameters
        ----------
        template :class:`str` | `Image.Image` | `Mat`:
            The template to find

        image :class:`str` | `Image.Image` | `Mat`:
            The image to find the template in

        confidence :class:`float`:
            How restrictive to be in whats considered a match

        grayscale :class:`bool`: [optional]
            Whehether to grayscale the template, default False

        convert :class:`bool`: [optional]
            Whehether to convert the template, default True

        center :class:`bool`: [optional]
            Whehether to get the matches center, default False

        Returns
        -------
        :class:`tuple[int, int]` | `tuple[int, int, int, int]:
            A tuple with the match either as centers or box
        """
        if convert:
            region = self.convert_region(region)
        haystack: np.ndarray = np.asarray(self.grab_screen(region, convert=False))  # type: ignore[arg-type]
        image_rgb = cv.cvtColor(haystack, cv.COLOR_BGR2RGB)
        img = Image.fromarray(image_rgb)
        box = pg.locate(
            self.convert_image(template) if convert else template,
            img,
            confidence=confidence,
            grayscale=grayscale,
        )
        if not box:
            return None

        box = (box[0] + region[0], box[1] + region[1], box[2], box[3])
        return get_center(box) if box and center else box

    def locate_all_template(
        self, template: str, region: tuple, confidence: float, convert: bool = True
    ):
        """Finds all locations of the given template on the screen."""
        return self.filter_points(
            set(
                pg.locateAllOnScreen(
                    self.convert_image(template),
                    region=self.convert_region(region) if convert else region,
                    confidence=confidence,
                )
            ),
            min_dist=15,
        )

    def filter_points(self, targets, min_dist) -> set:
        """Filters a set of points by min dist from each other.
        This is important because pyautogui may locate the same template
        multiple times on the same position.
        """
        filtered = set()

        while targets:
            eps = targets.pop()
            for point in targets:
                if all(abs(c2 - c1) < min_dist for c2, c1 in zip(eps, point)):
                    break
            else:
                filtered.add(eps)
        return filtered

    def denoise_text(
        self,
        image: str,
        denoise_rgb: tuple,
        variance: int,
        dilate: bool = True,
        upscale: bool = False,
        upscale_by: int = 8,
    ) -> Image.Image:
        """Denoises / Masks the passed image by the given RGB and variance.
        Useful to pre-process images for a tesseract character scan.

        Parameters:
        ----------
        image :class:`str` | `Image`:
            The image to denoise, if passed as string it will be read using cv2

        denoise_rgb :class:`tuple`:
            The rgb to filter out, only pixels with this rgb will remain in the image

        variance :class:`int`:
            The variance allowed for the denoise_rgb

        Returns:
        ----------
        An upscaled, filtered and dilated version of the given Image as Mat

        """
        # check if we need to read the image or convert it
        if isinstance(image, str):
            image = cv.imread(image, 1)
        else:
            image = np.asarray(image)

        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

        # set color range (filering the color of the chars here)
        lower_bound = (
            max(0, denoise_rgb[0] - variance),
            max(0, denoise_rgb[1] - variance),
            max(0, denoise_rgb[2] - variance),
        )
        upper_bound = (
            min(255, denoise_rgb[0] + variance),
            min(255, denoise_rgb[1] + variance),
            min(255, denoise_rgb[2] + variance),
        )

        # load the image into pillow to resize it
        img = cv.inRange(image, lower_bound, upper_bound)

        if not dilate:
            return img

        if upscale:
            img = Image.fromarray(img)
            img = img.resize((img.size[0] * upscale_by, img.size[1] * upscale_by), 1)

        matrix_size = 2 if not upscale else 3

        # Taking a matrix of size 5 as the kernel
        kernel = np.ones((matrix_size, matrix_size), np.uint8)
        return cv.dilate(np.asarray(img), kernel, iterations=1)
