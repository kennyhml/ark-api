from typing import Any, Optional

import cv2  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ..._ark import Ark
from ...exceptions import InventoryNotAccessibleError, NoGasolineError
from ...items import Item
from .._button import Button
from ..inventories import Inventory
from ..wheels import ActionWheel


class Structure(Ark):
    """Represents a structure in ARK.

    A structure provides access to it's inventory and allows to toggle
    it on or off, as well as check how many items were deposited into it
    and whats currently inside of it. The `name` does not have to match
    it's real in-game name, you may alter or enumerate the station names
    to keep track of different objects.

    Parameters
    ----------
    name :class:`str`:
        The name of the structure it represents.

    action_wheel :class:`ActionWheel | str`:
        The action wheel of the structure, either a previously created wheel
        or the filepath to the wheel image to create the wheel.

    inventory :class:`Inventory` [Optional]:
        The pre-created inventory of the structure, if not passed one will be created.

    craftables :class:`list[Item]` [Optional]:
        A list of items that can be crafted in the structure, onl to be passed if
        `inventory` was not.

    capacity :class:`str | int` [Optional]:
        The capacity of the structure, either as integer or a filepath leading
        to the file of the capped structure.

    toggleable :class:`bool`:
        Whether the structure can be turned on and off, `False` by default.

    Attributes:
    -----------
    TURN_ON :class:`Button`-
        A representation of the 'turn on' button for toggleable structures

    TURN_OFF :class:`Button`-
        A representation of the 'turn off' button for toggleable structures

    Properties:
    -----------
    name :class:`str`[get]:
        The name the structure was initialized with

    toggleable :class:`bool`[get]:
        Whether the structure is toggleable
    """

    TURN_ON = Button((956, 618), (740, 570, 444, 140), "turn_on.png")
    TURN_OFF = Button((956, 618), (740, 570, 444, 140), "turn_off.png")
    _ITEM_ADDED_REGION = (5, 850, 55, 230)

    def __init__(
        self,
        name: str,
        action_wheel: ActionWheel | str,
        inventory: Optional[Inventory] = None,
        craftables: Optional[list[Item]] = None,
        capacity: Optional[int | str] = None,
        *,
        toggleable: bool = False,
    ) -> None:
        super().__init__()
        if inventory and any((craftables, capacity)):
            raise ValueError(
                "Did not expect 'craftables' or 'capacity' alongside 'inventory'."
            )
        if isinstance(action_wheel, str):
            action_wheel = ActionWheel(name, action_wheel)
        if inventory is None:
            self.inventory = Inventory(name, craftables, capacity)
        else:
            self.inventory = inventory
        self.action_wheel = action_wheel
        self._name = name
        self._toggleable = toggleable

    def __str__(self) -> str:
        return f"Structure '{self._name}' of type '{type(self).__name__}'"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self._name}, inventory={self.inventory},"
            f"action_wheel={self.action_wheel}, toggleable={self._toggleable})"
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def toggleable(self) -> bool:
        return self._toggleable

    def open(self) -> None:
        """Wraps the inventory `open` function using the action wheel to
        validate whether we are actually in range of it on failure.

        Raises
        ------
        `InventoryNotAccessibleError`
            If the Inventory could not be accessed even though it is in
            range (determined by the action wheel)

        `WheelNotAccessibleError`
            When no wheel could be opened at all after several attempts

        `UnexpectedWheelError`
            When a wheel was opened but is of an unexpected entity
        """
        try:
            self.inventory.open()
        except InventoryNotAccessibleError:
            self.action_wheel.activate()
            self.action_wheel.deactivate()
            self.inventory.open(max_duration=40)

    def close(self) -> None:
        """Wraps the inventory `close` function."""
        self.inventory.close()

    def _get_amount_deposited(self, item: Item) -> int:
        """Checks how much of the given item was deposited. This is achieved
        by locating the items `added_icon` on the left side of the screen,
        and then doing some processing to get a region of interest of the
        amount that has been deposited.

        The image is then denoised, OCR'd and validated.

        Parameters
        ----------
        item :class:`Item`:
            The item to determine the amount of

        Returns
        -------
        :class:`int`:
            The amount of dust deposited, 0 on failure

        Example usage:
        ```py
        self._get_amount_deposited(DUST)
        >>> 2376
        ```
        """
        roi = self._get_item_amount_roi(item)
        if roi is None:
            return 0

        # grab the region of interest and apply denoising
        img = self.window.grab_screen(roi, convert=False)
        img = self.window.denoise_text(img, denoise_rgb=(255, 255, 255), variance=10)
        cv2.imshow("", img)
        cv2.waitKey(1)
        
        raw_result = tes.image_to_string(
            img,
            config="-c tessedit_char_whitelist=0123456789liIxObL --psm 7 -l eng",
        )
        return int(self._correct_ocr_mistakes(raw_result))

    def _get_item_amount_roi(self, item: Item) -> tuple[int, int, int, int] | None:
        """Returns the region of interest of a deposited item to determine the
        amount that was deposited.

        Parameters
        ----------
        item :class:`Item`:
            The item to determine the region of interest of

        Returns
        -------
        :class:`tuple[int, int, int, int]` | `None`:
            The region of interest as `x, y, w, h` or `None` on failure

        """
        if item.added_text is None:
            raise ValueError(f"Undefined 'added_text' for {item}!")

        if not (icon_pos := self._find_item_deposited(item)):
            return None

        # compute name roi
        text_start_x = icon_pos[0] + icon_pos[2]
        name_roi = (text_start_x + 130, icon_pos[1], 290, 40)
        name_text = self.window.locate_template(
            item.added_text,
            region=name_roi,
            confidence=0.7,
            convert=False,
        )
        # not worth trying to find out the amount without proper roi
        if name_text is None:
            return None

        # get our region of interest (from end of "Removed:" to start of "Element")
        return (name_roi[0], name_roi[1], int(name_text[0] - name_roi[0]), 40)

    def _correct_ocr_mistakes(self, raw: str) -> str:
        """Corrects 'expected' or common tesseract mistakes."""
        # replace all the mistaken "1"s
        for char in ["I", "l", "i", "b", "L"]:
            raw = raw.replace(char, "1")

        # replace mistaken "0"s, strip off newlines
        filtered = raw.replace("O", "0").rstrip()

        # find the x to slice out the actual number
        x = filtered.find("x")
        if any((not filtered, x == -1, filtered == "x")):
            return "0"

        return filtered[:x]

    def _find_item_deposited(self, item: Item) -> Any:
        """Returns the position of a deposited item. The `Item` must have a
        `added_icon` defined, otherwise a `ValueError` is raised."""
        if item.added_icon is None:
            raise ValueError(f"Undefined 'added_icon' for {item}!")

        return self.window.locate_template(
            item.added_icon, region=self._ITEM_ADDED_REGION, confidence=0.7
        )

    def _find_turn_on_text(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/turn_on.png",
                (0, 0, 1920, 1080),
                confidence=0.92,
            )
            is not None
        )

    def _find_turn_off_text(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/turn_off.png",
                (0, 0, 1920, 1080),
                confidence=0.92,
            )
            is not None
        )

    def turn_on(self) -> None:
        """Turns the structure on, if not inside an inventory, it will first
        look for the 'TURN ON' text to toggle the structure from outside.

        Otherwise the inventory will be opened (if it is not already), and
        the structure will be toggled through the inventory.

        Raises a `NoGasolineError` if the structure cannot be turned on.
        """
        if not self.inventory.is_open() and self._find_turn_on_text():
            self.press(self.keybinds.use)
            self.sleep(0.3)
            return

        self.inventory.open()
        if self.is_turned_on():
            return

        if not self.is_turned_off():
            raise NoGasolineError(self._name)

        while self.is_turned_off():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

    def turn_off(self) -> None:
        """Turns the structure off, assumes it is already opened."""

        if not self.inventory.is_open() and self._find_turn_off_text():
            self.press(self.keybinds.use)
            self.sleep(0.3)
            return

        self.inventory.open()
        if self.is_turned_off():
            return

        while self.is_turned_on():
            self.click_at(964, 615, delay=0.3)
            self.sleep(1)

    def is_turned_on(self) -> bool:
        """Return whether the Structure is turned on."""
        if not self._toggleable:
            raise ValueError(f"{self} is not toggleable!")
        return self.inventory.locate_button(
            self.TURN_OFF, grayscale=True, confidence=0.85
        )

    def is_turned_off(self) -> bool:
        """Return whether the Structure can be turned on."""
        return self.inventory.locate_button(
            self.TURN_ON, grayscale=True, confidence=0.85
        )
