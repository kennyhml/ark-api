import functools
import math
import os
import time
from inspect import signature
from pathlib import Path
from threading import Thread
from typing import Any, Callable

import psutil  # type: ignore[import]
import win32clipboard  # type: ignore[import]

from .exceptions import TerminatedError
from .state import State


def state_checker(func: Callable):
    """Checks on the Threads state before executing"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while State.paused:
            time.sleep(0.1)

        if not State.running:
            raise TerminatedError
        return func(*args, **kwargs)

    return wrapper

def get_filepath(filepath: str) -> str:
    """Validates the given filepath to allow to adjust files to the package
    path as well as loading files from the relative bot files."""
    if os.path.exists(filepath):
        return filepath.replace("/", "\\")

    abs_path = os.path.join(str(Path(__file__).parent), filepath)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Could not find {filepath} anywhere.")
    return abs_path.replace("/", "\\")


def timedout(timer: float, max_time: int | float) -> bool:
    """Checks whether the given timer has exceeded the maximum time"""
    return (time.time() - timer) > max_time


def yes_no(boolean_value: bool) -> str:
    return ["No", "Yes"][boolean_value]


def threaded(name: str):
    """Threads a function, beware that it will lose its return values"""

    def outer(func: Callable):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            thread = Thread(target=func, name=name, args=args, kwargs=kwargs)
            thread.start()

        return inner

    return outer


def await_event(
    func: Callable,
    expected_return_value: Any = True,
    max_duration: int | float = 5,
    ignore_annotation: bool = False,
) -> bool:
    """Awaits for the given function to return an expected value.
    Returns whether the function returned the value in the expected time.
    """

    @state_checker
    def sleep(s):
        time.sleep(s)
    if not func.__name__ == "<lambda>":
        log_str = f"Awaiting function '{func.__name__}' "
    else:
        log_str = f"Awaiting function '{func.__qualname__}' "
    if hasattr(func, "__self__"):
        log_str += f"of '{type(func.__self__).__name__}' "
    log_str += f"to return '{expected_return_value}' within {max_duration}s"
    # print(log_str)

    return_type = signature(func).return_annotation
    assert (
        return_type == type(expected_return_value) or ignore_annotation
    ), "Functions return type does not match expected return type."

    counter = 0
    while not func() == expected_return_value:
        counter += 1
        sleep(0.05)

        if (counter / 20) > max_duration:
            return False
    return True


def ark_is_running() -> bool:
    """Checks if the passed process is running"""
    return "ARK: Survival Evolved" in [
        process.name() for process in psutil.process_iter()
    ]


def close_ark() -> None:
    for process in psutil.process_iter():
        if process.name() == "ARK: Survival Evolved":
            process.kill()


def get_center(box: tuple[int, int, int, int]) -> tuple[int, int]:
    """Gets the center of a region (x, y, width, height)
    Parameters
    ----------
    box :class: `tuple[int, int, int, int]`:
        The box to get the center of
    Returns
    -------
    :class:`tuple[int, int]`:
        The center of the box
    """
    return int(box[0] + (box[2] / 2)), int(box[1] + (box[3] / 2))


def filter_points(points: set, minimum_distance: int) -> set:
    """Filters a set of points until there are no points left that are
    closer to each other than the given minimum distance
    Parameters
    ----------
    points :class:`set`:
        The set of points to filter
    minimum_distance :class:`int`:
        The minimum distance the points need to have to each other
    Returns
    -------
    :class:`set`:
        A set of the filtered points
    """
    filtered = set()

    while points:
        eps = points.pop()
        for point in points:
            if all(abs(c2 - c1) < minimum_distance for c2, c1 in zip(eps, point)):
                break
        else:
            filtered.add(eps)
    return filtered


def set_clipboard(text):
    """Puts the passed text into the clipboard to allow for pasting"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_TEXT)
    win32clipboard.CloseClipboard()


def format_seconds(seconds: int) -> str:
    """Formats a number in seconds to a string nicely displaying it in
    different formats."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes = round(days), round(hours), round(minutes)
    if days:
        return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    elif hours:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    elif minutes:
        return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
    else:
        return f"{seconds} seconds"


def find_center(pixels: list[tuple[int, int]]) -> tuple[int, int]:
    """Finds the 'center of mass' given an iterable of points"""
    x_total = 0
    y_total = 0

    # sum up all the x and y points
    for x, y in pixels:
        x_total += x
        y_total += y

    # get the "average" point
    center_x = round(x_total / len(pixels))
    center_y = round(y_total / len(pixels))
    return center_x, center_y


def find_closest_pixel(
    pixels: list[tuple[int, int]], center: tuple[int, int]
) -> tuple[int, int]:
    """Finds the pixel closest to the center"""
    closest_pixel = pixels[0]
    closest_distance = float("inf")

    for pixel in pixels:
        distance = math.sqrt((pixel[0] - center[0]) ** 2 + (pixel[1] - center[1]) ** 2)
        if distance < closest_distance:
            # set new closest distance
            closest_pixel = pixel
            closest_distance = distance
    return closest_pixel
