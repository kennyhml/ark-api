import math
import time
from typing import Iterable, Literal, Optional, final, overload

import pathlib
import cv2 as cv  # type: ignore
import numpy as np
import pyautogui as pg  # type: ignore[import]
from pytesseract import pytesseract as tes  # type: ignore[import]

from ... import config
from ..._ark import Ark
from ..._helpers import await_event, get_center, get_filepath, set_clipboard, timedout
from ...exceptions import (
    InventoryNotAccessibleError,
    InventoryNotClosableError,
    InventoryNotOpenError,
    NoItemsAddedError,
    ReceivingRemoveInventoryTimeout,
    UnknownFolderIndexError,
    EggStatError,
    ContextActionError,
    FolderError,
)
from ...items import Item
from .._button import Button


class Inventory(Ark):
    """Represents an inventory in Ark.

    All `Structure` and `Dinosaur` objects contain an `Inventory` attribute,
    it is responsible for all action related to transferring items, clicking
    buttons within the inventory and using the searchbar.

    For inventories that contain `craftables`, it also provides the methods
    needed to use the crafting tab and craft requested items. Furthermore,
    it is able to keep track and sync it's contents.

    Parameters:
    -----------
    entity :class:`str`:
        The name of the structure / dino the inventory belongs to

    craftables :class:`list[Item]` [Optional]:
        A list of items that can be crafted in the in the crafting tab

    capacity :class:`str`: [Optional]
        An image path containing the image of the max capacity.

    Properties:
    ----------
    contents :class:`dict[Item, int]`:
        A dictionary mapping items in the structure to their quantity

    capacity :class:`int`:
        The set maximum slots the inventory can hold

    craftables :class:`list[Item]`:
        A list of items that can be crafted in the inventories crafting tab.
    """

    LAST_TRANSFER_ALL = time.time()
    SLOTS = [
        (x, y, 93, 93) for y in range(232, 883, 93) for x in range(1243, 1708 + 93, 93)
    ]
    LEVEL_UP_BUTTONS = {
        "health": (1150, 515),
        "stamina": (1150, 558),
        "oxygen": (1150, 600),
        "food": (1151, 645),
        "weight": (1149, 688),
        "melee": (1150, 730),
        "speed": (1151, 773),
        "crafting": (1149, 818),
    }
    CRAFTING_QUEUE = (1234, 779, 571, 168)

    _FOLDERS = [
        "AAA",
        "BBB",
        "CCC",
        "DDD",
        "EEE",
        "FFF",
        "GGG",
        "HHH",
        "III",
        "JJJ",
        "KKK",
    ]

    _FOLDER_VIEW = Button((1663, 188), (1632, 158, 61, 56), "folder_view.png")
    _SHOW_ENGRAMS = Button((1716, 189), (1690, 160, 51, 51), "show_engrams.png")
    _UNL_ENGRAMS = Button((1770, 188), (1742, 160, 56, 54), "unlearned_engrams.png")
    _TRANSFER_ALL = Button((1425, 190))
    _DROP_ALL = Button((1477, 187))
    _CRAFTING_TAB = Button((1716, 118), (1627, 82, 211, 69), "crafting.png")
    _INVENTORY_TAB = Button((1322, 118), (1235, 88, 184, 60), "inventory.png")
    _CREATE_FOLDER = Button((1584, 187))
    _STOP_CRAFTING = Button((1775, 800), (1750, 775, 53, 56), "cancel_craft.png")
    _LEVEL_UP = Button((1150, 515), (1227, 494, 45, 45), "level_up.png")

    _SEARCHBAR = (1300, 190)
    _ADDED_REGION = (40, 1020, 360, 60)
    _ITEM_REGION = (1243, 232, 562, 710)
    _UPPER_ITEM_REGION = (1240, 230, 568, 191)
    _SLOTS_REGION = (1074, 500, 60, 23)
    _REMOTE_INVENTORY = (1346, 563, 345, 43)
    _CAPPED_ICON = (1210, 230, 55, 54)

    def __init__(
        self,
        entity_name: str,
        craftables: Optional[list[Item]] = None,
        capacity: Optional[str | int] = None,
    ) -> None:
        super().__init__()
        self._name = entity_name
        self._capacity = capacity
        self._craftables = craftables
        if isinstance(capacity, str):
            self._capacity = get_filepath(capacity)

        self._contents: dict[str, int] = {}

    def __str__(self) -> str:
        return f"Inventory of {self._name} with max slots {self._capacity}"

    @property
    def contents(self) -> dict[str, int]:
        return self._contents

    @property
    def capacity(self) -> int | str | None:
        return self._capacity

    @property
    def craftables(self) -> list[Item] | None:
        return self._craftables

    @property
    def name(self) -> str:
        return self._name

    @final
    def add_contents(self, item: Item, stacks: int) -> None:
        try:
            self._contents[item.name] += stacks
        except KeyError:
            self._contents[item.name] = stacks

    @final
    def set_content(self, item: Item, stacks: Optional[int] = None) -> None:
        if stacks is not None:
            self._contents[item.name] = stacks
        else:
            self._contents[item.name] = self.count(item)

    @final
    def locate_button(self, button: Button, **kwargs) -> bool:
        assert button.template is not None and button.region is not None
        return (
            self.window.locate_template(button.template, button.region, **kwargs)
            is not None
        )

    def is_open(self) -> bool:
        """Checks if the inventory is open."""
        return self.locate_button(
            self._INVENTORY_TAB, confidence=0.8
        ) or self.locate_button(self._CRAFTING_TAB, confidence=0.8)

    def open(self, default_key: bool = True, max_duration: int = 10) -> None:
        """Opens the inventory using the 'target inventory' keybind by default.

        Set `default_key` to `False` to use 'E' instead, which will allow to access
        entities in weird spots.

        Beware that using the non-default key regularly is not recommended.

        Raises:
        ----------
        `InventoryNotAccessibleError`
            If the inventory could not be opened within the max duration
        """
        attempts = 0
        while not self.is_open():
            while self.last_view_changed is not None and not timedout(
                self.last_view_changed, 0.5
            ):
                self.sleep(0.1)
            attempts += 1

            key = self.keybinds.target_inventory if default_key else self.keybinds.use
            self.press(key)

            if await_event(self.is_open, max_duration=config.INVENTORY_OPEN_INTERVAL):
                break

            if attempts >= (
                max_duration * config.TIMER_FACTOR / config.INVENTORY_OPEN_INTERVAL
            ):
                raise InventoryNotAccessibleError(self)
        self._await_receiving_remove_inventory()

    def close(self) -> None:
        """Closes the inventory using the 'target inventory' keybind.

        Raises:
        ----------
        `InventoryNotClosableError` if the inventory did not close
        within 30 seconds, indicating a server / game crash.
        """
        attempts = 0
        while self.is_open():
            attempts += 1

            self.press(self.keybinds.target_inventory)
            if await_event(
                self.is_open, False, max_duration=config.INVENTORY_CLOSE_INTERVAL
            ):
                break

            if attempts > (40 * config.TIMER_FACTOR / config.INVENTORY_OPEN_INTERVAL):
                raise InventoryNotClosableError(self)
        Ark.last_interface_exit = time.time()
        self.sleep(0.3)

    @overload
    def scroll(self, way: Literal["up", "down"], *, rows: int = 1) -> None: ...

    @overload
    def scroll(self, way: Literal["up", "down"], *, pages: int = 0) -> None: ...

    @final
    def scroll(
        self, way: Literal["up", "down"], *, rows: int = 1, pages: int = 0
    ) -> None:
        """Scrolls up or down the inventory by a given amount of rows or pages.

        Parameters
        ----------
        way :class:`Literal["up", "down"]`:
            The direction to scroll, either up or down.

        rows :class:`int`:
            The number of rows to scroll, default 1

        pages :class:`int`:
            Alternative to `rows`, scroll by page rather than row. 1 page = 7 rows.
        """
        if way not in ["up", "down"]:
            raise ValueError(f'Expected one of {["up", "down"]}, got "{way}".')

        if not self.is_open():
            raise InventoryNotOpenError

        if pages:
            rows = pages * 7

        for _ in range(rows):
            self.mouse_scroll(2.91 * (1 if way == "up" else -1))

    @final
    def search(self, item: Item | str, delete_prior: bool = True) -> None:
        """Searches for an item or word in the searchbar. Then presses
        escape to tab back out of the spacebar.

        Parameters
        ----------
        items :class:`Item | str`:
            The item or term to search for
        """
        if not self.is_open():
            raise InventoryNotOpenError

        self._click_searchbar(delete_prior)
        # lowercasing the term because pyautogui has a weird gist where it will
        # actually use shift + letter to capitalize it, which opens the chat somehow
        if isinstance(item, str):
            if "*" in item:
                set_clipboard(item)
                self.sleep(0.3)
                pg.hotkey("ctrl", "v", interval=0.2)
            else:
                pg.typewrite(item.lower(), interval=0.001)
        else:
            pg.typewrite(item.search_name.lower(), interval=0.001)

        # escape out of the searchbar so presing f closes the inventory
        self.sleep(0.2)
        self.press("esc")

    @final
    def drop_all(self, items: Optional[Iterable[Item | str]] = None) -> None:
        """Searches for an iterable of Items or words and drops all. If no
        items are passed, it simply drops without searching for anything.

        Parameters
        ----------
        items :class:`Iterable[Item | str]`: [Optional]
            An iterable of items to search for, then drop
        """
        if not self.is_open():
            raise InventoryNotOpenError

        if items is None:
            self.click_at(self._DROP_ALL.location)
            return

        # already know someone isnt gonna check the typehints and pass
        # an item or string on its own :D
        if not isinstance(items, Iterable):
            items = {items}
        else:
            items = set(items)

        for item in items:
            self.search(item)
            self.click_at(self._DROP_ALL.location)

    @final
    def transfer_all(
        self,
        items: Optional[Iterable[Item | str] | Item | str] = None,
        delete_search: bool = True,
        enforce_from_slot: int | None = None,
    ) -> None:
        """Searches for an iterable of Items or words and transfers all. If no
        items are passed, it simply transfers all without searching for anything.

        Parameters
        ----------
        items :class:`Iterable[Item | str]`: [Optional]
            An iterable of items to search for, then transfer
        """
        if not self.is_open():
            raise InventoryNotOpenError

        def press_button() -> None:
            start = time.time()
            while enforce_from_slot is None or not self.is_empty(enforce_from_slot):
                if (time.time() - self.LAST_TRANSFER_ALL) < 5:
                    self.sleep(0.1)
                    continue

                if (
                    items is None
                    and enforce_from_slot is not None
                    and timedout(start, 5)
                    and self.is_in_folder()
                ):
                    last_filled_row = 6
                    # got the folder glitch, transferring all wont work..
                    prev = pg.PAUSE
                    pg.PAUSE = 0
                    try:
                        while not self.is_empty(enforce_from_slot):
                            self.window.begin_snapshot()
                            for row in range(last_filled_row, -1, -1):
                                first_slot = row * 6
                                if row != 0 and self.is_empty(first_slot):
                                    continue
                                last_filled_row = max(last_filled_row, row)

                                for slot in range(5, -1, -1):
                                    area = self.SLOTS[first_slot + slot]
                                    self.move_to(get_center(area))
                                    if row == 0:
                                        self.sleep(0.05)
                                    self.press(self.keybinds.transfer)
                                    self.sleep(0.01)
                            self.window.end_snapshot()
                            self.sleep(0.2)
                    finally:
                        pg.PAUSE = prev
                        self.window.end_snapshot()
                    continue

                self.click_at(self._TRANSFER_ALL.location, delay=0.2)
                Inventory.LAST_TRANSFER_ALL = time.time()
                if enforce_from_slot is None:
                    break

        if items is None:
            press_button()
            return

        # already know someone isnt gonna check the typehints and pass
        # an item or string on its own :D
        if isinstance(items, (str, Item)):
            items = {items}
        else:
            items = set(items)

        for item in items:
            self.search(item, delete_prior=delete_search or len(items) > 1)

            press_button()

    @final
    def open_tab(self, tab: Literal["inventory", "crafting"]) -> None:
        """Opens the requested tab, either the inventory or crafting. Ensures
        the inventory is open before doing so to avoid punching.

        Parameters
        ----------
        tab :class:`Literal["inventory", "crafting"]`:
            The tab to open
        """
        if not self.is_open():
            raise InventoryNotOpenError

        if tab == "crafting":
            self.click_at(self._CRAFTING_TAB.location, delay=0.3)
        elif tab == "inventory":
            self.click_at(self._INVENTORY_TAB.location, delay=0.3)
        else:
            raise ValueError(f"Expected one of ['inventory', 'crafting'], got {tab}")
        self.sleep(1)

    @final
    def drop(self, item: Item, search: bool = True) -> None:
        """Searches for the given item and popcorns it until there is none left.

        Parameters
        ----------
        item :class:`Item`:
            The item to be popcorned
        """
        if not self.is_open():
            raise InventoryNotOpenError

        if search:
            self.search(item)

        while position := self.find(item, is_searched=search):
            self.move_to(position)
            self.press(self.keybinds.drop)

    @final
    def count(self, item: Item) -> int:
        """Returns the amount of stacks of the given item located within the inventory."""
        return len(
            self.window.locate_all_template(
                item.inventory_icon,
                region=self._ITEM_REGION,
                confidence=0.85,
                grayscale=True,
            )
        )

    @final
    def find(self, item: Item, is_searched: bool = False) -> tuple[int, int] | None:
        """Returns the position of the given item within the inventory.

        Beware that the item is grayscaled to make it compatible
        across qualities.

        Parameters:
        ------------
        item :class:`Item`:
            The item object of the item to check for
        """
        return self.window.locate_template(
            item.inventory_icon,
            region=self._UPPER_ITEM_REGION if is_searched else self._ITEM_REGION,
            confidence=0.8,
            center=True,
            grayscale=True,
        )

    @final
    def has(self, item: Item, is_searched: bool = False) -> bool:
        """Returns whether the player inventory has an item.

        Beware that the item is grayscaled to make it compatible
        across qualities.

        Parameters:
        ------------
        item :class:`Item`:
            The item object of the item to check for

        Returns whether the item is in the inventory or not.
        """
        return self.find(item, is_searched) is not None

    @overload
    def take(self, item: Item, *, amount: int) -> None: ...

    @overload
    def take(self, item: Item, *, stacks: int) -> None: ...

    @final
    def take(self, item: Item, *, stacks: int = 0, amount: int = 1) -> None:
        """Searches the given item and takes one.

        Parameters:
        -----------
        item :class:`Item`:
            The item object to search for

        stacks :class:`int`:
            The amount of stacks to take of the item

        Raises:
        -------
        `NoItemsAddedError`
            When a stack could not be transferred within 30 seconds after
            pressing 'T'

        """
        # search for the item and hit take all
        if not self.find(item):
            self.search(item)
        self.sleep(0.2)

        # take a specific quantity of a stack
        if not stacks:
            pos = self.find(item)
            if pos is None:
                return
            self.click_at(pos)

            for _ in range(amount):
                pg.click(clicks=2)

            return

        # take stacks only, using T-transfers
        for stack in range(stacks):
            if (pos := self.find(item)) is None:
                return

            before_take = self.count(item)
            if not stack:
                self.click_at(pos)
            self.press(self.keybinds.transfer)
            try:
                self._receive_stack(item, before_take)
            except NoItemsAddedError:
                continue

    @overload
    def manage_view_option(
        self,
        option: Literal["folder view", "show engrams", "unlearned engrams"],
    ) -> bool: ...

    @overload
    def manage_view_option(
        self,
        option: Literal["folder view", "show engrams", "unlearned engrams"],
        *,
        set_to: bool,
    ) -> None: ...

    def manage_view_option(
        self,
        option: Literal["folder view", "show engrams", "unlearned engrams"],
        *,
        set_to: Optional[bool] = None,
    ) -> bool | None:
        """Manages the inventories view option buttons. If `set_to` is not passed,
        it simply returns whether a given option is currently enabled.

        Parameters
        ----------
        option :class:`Literal["folder view", "show engrams", "unlearned engrams"]`:
            The option to check or change

        set_to :class:`Optional[bool]`:
            The state to set the option to, `None` by default
        """
        if option not in ["folder view", "show engrams", "unlearned engrams"]:
            raise ValueError(
                f'Expected one of {["folder view", "show engrams", "unlearned engrams"]}, got {option}'
            )

        if not self.is_open():
            raise InventoryNotOpenError

        buttons = {
            "folder view": self._FOLDER_VIEW,
            "show engrams": self._SHOW_ENGRAMS,
            "unlearned engrams": self._UNL_ENGRAMS,
        }
        state = self.locate_button(buttons[option], confidence=0.8)
        if set_to is None:
            return state

        if state != set_to:
            self.click_at(buttons[option].location)
        return None

    @final
    def is_capped(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/capped.png",
                region=self._CAPPED_ICON,
                confidence=0.75,
                grayscale=True,
            )
            is not None
        )

    @final
    def is_crafting(self) -> bool:
        return self.locate_button(self._STOP_CRAFTING, confidence=0.7)

    @final
    def has_level_up(self) -> bool:
        return pg.pixelMatchesColor(1161, 524, (0, 0, 0), tolerance=3)

    def level_skill(self, skill: str, times: int) -> None:
        pos = self.LEVEL_UP_BUTTONS[skill]
        self.move_to(pos)

        for _ in range(times):
            pg.click()

    def stop_crafting(self) -> None:
        if not self.is_crafting():
            self.click_at(self._STOP_CRAFTING.location)

    def select_slot(self, idx: int = 0) -> None:
        """Moves to the first slot"""
        self.move_to(get_center(self.SLOTS[idx]))

    def get_folder_index(self) -> int:
        """Returns the number of the crop plot in the stack by checking for
        the folder name from AAA to HHH, being 1 to 9."""
        for _ in range(3):
            for index, option in enumerate(self._FOLDERS, start=1):
                if self.window.locate_template(
                    f"{self.PKG_DIR}/assets/interfaces/folder_{option}.png",
                    region=(1240, 290, 55, 34),
                    confidence=0.9,
                ):
                    return index
            self.sleep(0.5)
        raise UnknownFolderIndexError(self)

    def read_folder_name(self, slot: int, config: str) -> str:
        name_roi = (self.SLOTS[slot][0], self.SLOTS[slot][1] + 68, 81, 25)

        img = self.window.grab_screen(name_roi)
        img = np.asarray(img)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        mask1 = cv.inRange(hsv, (97, 190, 160), (180, 255, 255))
        resized = cv.resize(mask1, None, fx=4, fy=4, interpolation=cv.INTER_LINEAR)
        inverted = cv.bitwise_not(resized)
        padded = cv.copyMakeBorder(
            inverted, 20, 20, 20, 20, cv.BORDER_CONSTANT, value=255
        )
        result: str = tes.image_to_string(padded, config=config).rstrip()
        return result

    def is_folder(self, slot: int, folder: str | None = None) -> bool:
        roi = (self.SLOTS[slot][0], self.SLOTS[slot][1], 54, 30)
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/folder.png",
                region=roi,
                confidence=0.7,
            )
            is not None
        )

    def is_in_folder(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/in_folder.png",
                region=self.SLOTS[0],
                confidence=0.7,
            )
            is not None
        )

    def open_folder(self, slot: int):
        loc = self.SLOTS[slot]
        self.move_to(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
        self.sleep(0.1)

        start = time.time()
        last_click = None
        while not self.is_in_folder():
            if timedout(start, 15):
                raise FolderError("open")

            if last_click is None or timedout(last_click, 3):
                for _ in range(2):
                    self.click("left")
                    self.sleep(0.1)
                last_click = time.time()

                # make sure we dont keep hovering the slot if it isn the first
                if slot > 1:
                    self.sleep(0.3)
                    self.select_slot(0)

    def close_current_folder(self):
        loc = self.SLOTS[0]
        self.move_to(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
        self.sleep(0.1)

        start = time.time()
        last_click = None
        while self.is_in_folder():
            if timedout(start, 15):
                raise FolderError("close")

            if last_click is None or timedout(last_click, 1):
                for _ in range(2):
                    self.click("left")
                    self.sleep(0.1)
                last_click = time.time()

    def is_baby_cryo(self, slot: int) -> bool:
        roi = (self.SLOTS[slot][0], self.SLOTS[slot][1], 46, 46)

        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/baby.png",
                region=roi,
                confidence=0.7,
            )
            is not None
        )

    def is_cryo_female(self, slot: int) -> bool:
        roi = (self.SLOTS[slot][0] + 22, self.SLOTS[slot][1] + 26, 58, 53)

        img = self.window.grab_screen(roi)
        masked = self.window.denoise_text(
            img, (250, 172, 252), variance=27, dilate=False
        )

        return cv.countNonZero(masked) > 5

    def is_cryo_ready_to_breed(self, slot: int) -> int:
        loc = self.SLOTS[slot]
        self.move_to(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
        time.sleep(0.1)

        img = self.window.grab_screen((916, 0, 1003, 1079))
        masked = self.window.denoise_text(
            img, (244, 236, 175), variance=45, dilate=True
        )
        img = np.asarray(img)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        contours, _ = cv.findContours(masked, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        popup = None

        for cnt in contours:
            peri = cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, 0.02 * peri, True)
            area: int = cv.contourArea(cnt)

            if len(approx) == 4 and area > 150000 and area < 500000:
                x, y, w, h = cv.boundingRect(approx)
                cropped_roi = np.asarray(img)[y : y + h, x : x + w]

                if self.window.locate_in_image(
                    f"{self.PKG_DIR}/assets/stats/health.png",
                    cropped_roi,
                    confidence=0.7,
                ):
                    popup = cropped_roi
                    break
        if popup is None:
            raise

        return self.window.locate_in_image(
            f"{self.PKG_DIR}/assets/interfaces/ready_to_mate.png",
            popup,
            confidence=0.7,
        )

    def get_baby_time_left(self, slot: int) -> int:
        loc = self.SLOTS[slot]
        self.move_to(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
        time.sleep(0.1)

        img = self.window.grab_screen((916, 0, 1003, 1079))
        masked = self.window.denoise_text(
            img, (244, 236, 175), variance=45, dilate=True
        )
        img = np.asarray(img)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        contours, _ = cv.findContours(masked, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        popup = None

        for cnt in contours:
            peri = cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, 0.02 * peri, True)
            area: int = cv.contourArea(cnt)

            if len(approx) == 4 and area > 150000 and area < 500000:
                x, y, w, h = cv.boundingRect(approx)
                cropped_roi = np.asarray(img)[y : y + h, x : x + w]

                if self.window.locate_in_image(
                    f"{self.PKG_DIR}/assets/stats/health.png",
                    cropped_roi,
                    confidence=0.7,
                ):
                    popup = cropped_roi
                    break
        if popup is None:
            raise

        nursing = self.window.locate_in_image(
            f"{self.PKG_DIR}/assets/interfaces/nursing.png",
            popup,
            confidence=0.7,
        )
        if nursing is None:
            raise

        x, y, w, h = (nursing[0] + nursing[2] + 5, nursing[1] + 12, 100, 19)
        raise_time_crop = popup[y : y + h, x : x + w]
        hsv = cv.cvtColor(raise_time_crop, cv.COLOR_BGR2HSV)

        mask1 = cv.inRange(hsv, (95, 112, 215), (110, 146, 255))
        resized = cv.resize(mask1, None, fx=4, fy=4, interpolation=cv.INTER_LINEAR)

        custom_config = r"--psm 7 -c tessedit_char_whitelist=0123456789:"
        extracted_time = tes.image_to_string(resized, config=custom_config)
        result = extracted_time.strip()
        print(f"ocr raise timer: {result}")

        sections = result.split(":")
        if len(sections) == 1:
            seconds = sections[0]
            return int(seconds)
        if len(sections) == 2:
            minutes, seconds = sections
            return int(minutes) * 60 + int(seconds)
        if len(sections) == 3:
            hours, minutes, seconds = sections
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        raise ValueError(f"Could not parse raise time {result}")

    def do_content_actions(self, slot: int, actions: list[str]) -> None:
        roi = (self.SLOTS[slot][0], self.SLOTS[slot][1] + self.SLOTS[slot][3], 258, 214)
        area = self.SLOTS[slot]

        for i, action in enumerate(actions):
            start = time.time()
            while True:
                if timedout(start, 5):
                    raise ContextActionError(action)

                if i == 0:
                    self.click_at(
                        area[0] + area[2] / 2, area[1] + area[3] / 2, button="right"
                    )
                    self.sleep(0.3)

                loc = self.window.locate_template(
                    f"{self.PKG_DIR}/assets/interfaces/{action}.png",
                    region=roi,
                    confidence=0.7,
                )

                if loc is not None:
                    if action == "send_to":
                        self.move_to(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
                    else:
                        self.click_at(loc[0] + loc[2] / 2, loc[1] + loc[3] / 2)
                    self.sleep(0.5)
                    break
                elif (
                    slot % 6 == 5
                    and action == "nearest_incubator"
                    and timedout(start, 3)
                ):
                    self.click("left")
                    self.sleep(0.5)
                    break

    def is_empty(self, slot: int) -> bool:
        """Checks if a slot is empty"""
        roi = (self.SLOTS[slot][0] + 69, self.SLOTS[slot][1] + 76, 27, 15)
        img = self.window.grab_screen(roi)
        masked = self.window.denoise_text(
            img,
            (255, 205, 56),
            dilate=False,
            variance=5,
        )

        count = cv.countNonZero(masked)
        return count < 5

    def get_egg_stats(self, slot: int, **kwargs) -> dict[str, dict | str]:
        area = self.SLOTS[slot]
        self.move_to(area[0] + area[2] / 2, area[1] + area[3] / 2)
        self.sleep(0.3)

        # displays in a different loc depending on the slot
        flipped = slot % 6 in (4, 5)
        if slot <= 5:
            if flipped:
                roi = (area[0] - 304, area[1], 300, 367)
            else:
                roi = (area[0] + 98, area[1], 300, 367)
        else:
            if flipped:
                roi = (area[0] - 304, area[1] - 282, 300, 367)
            else:
                roi = (area[0] + 98, area[1] - 282, 300, 367)

        start = time.time()
        female_stat_color = (191, 127, 255)
        male_stat_color = (253, 190, 0)
        muta_color = (64, 252, 63)
        name_color = (250, 249, 245)

        while True:
            if timedout(start, 3):
                raise EggStatError("Could not hover the egg")

            img = self.window.grab_screen(roi)

            mat = np.asarray(img)
            mat = cv.cvtColor(mat, cv.COLOR_RGB2BGR)
            mat = cv.cvtColor(mat, cv.COLOR_BGR2RGB)

            nx, ny, nw, nh = (144, 40, 144, 25)
            name_crop = mat[ny : ny + nh, nx : nx + nw]
            name_mask = self.window.denoise_text(
                name_crop, name_color, variance=30, dilate=False
            )
            if cv.countNonZero(name_mask) > 50:
                break

        gx, gy, gw, gh = (99, 118, 24, 30)
        ix, iy, iw, ih = (144, 40, 144, 25)

        gender_crop = mat[gy : gy + gh, gx : gx + gw]
        incubation_crop = mat[iy : iy + ih, ix : ix + iw]

        ret: dict[str, dict | str] = {}

        for k, v in kwargs.items():
            if k == "maturation":
                # todo: check maturation percentage
                ...
            elif k == "gender":
                if (
                    self.window.locate_in_image(
                        f"{self.PKG_DIR}/assets/stats/female.png",
                        gender_crop,
                        confidence=0.7,
                    )
                    is not None
                ):
                    ret["gender"] = "female"
                elif (
                    self.window.locate_in_image(
                        f"{self.PKG_DIR}/assets/stats/male.png",
                        gender_crop,
                        confidence=0.7,
                    )
                    is not None
                ):
                    ret["gender"] = "male"
                else:
                    raise EggStatError("Could not determine a gender")
            else:
                stat_img = f"{self.PKG_DIR}/assets/stats/{k}.png"
                if not pathlib.Path(stat_img).exists():
                    raise ValueError(f"Invalid kwarg: {k}")

                loc = self.window.locate_in_image(
                    stat_img,
                    mat,
                    confidence=0.85,
                )
                if loc is None:
                    raise EggStatError(f"Could not find stat {k}")

                roi = (loc[0] + loc[2] + 2, loc[1], 76, 28)
                x, y, w, h = roi
                crop = mat[y : y + h, x : x + w]

                male_mask = self.window.denoise_text(
                    crop, male_stat_color, variance=30, dilate=False
                )
                female_mask = self.window.denoise_text(
                    crop, female_stat_color, variance=30, dilate=False
                )
                muta_mask = self.window.denoise_text(
                    crop, muta_color, variance=30, dilate=False
                )
                is_male = cv.countNonZero(male_mask) > 10
                is_female = cv.countNonZero(female_mask) > 10
                is_muta = is_male and cv.countNonZero(muta_mask) > 10
                is_double_muta = (
                    is_muta
                    and self.window.locate_in_image(
                        f"{self.PKG_DIR}/assets/stats/muta.png",
                        crop,
                        confidence=0.9,
                    )
                    is None
                )

                if v == "muta":
                    ret[k] = {"satisfied": is_muta, "double": is_double_muta}
                if v == "male":
                    ret[k] = {"satisfied": is_male}
                if v == "female":
                    ret[k] = {"satisfied": is_female}

        return ret

    def create_folder(self, name: str) -> None:
        """Creates a folder in the inventory at the classes folder button"""
        if not self.is_open():
            raise InventoryNotOpenError

        set_clipboard(name)

        self.click_at(1585, 187)
        self.sleep(0.3)
        pg.hotkey("ctrl", "v", interval=0.2)
        self.sleep(0.3)
        self.press("enter")
        self.sleep(0.3)
        # self.click_at(961, 677)
        # self.click("left")

    def craft(self, item: Item, amount: int) -> None:
        """Crafts the given amount of the given item. Spams 'A' if
        there is more than 50 to craft.
        """
        self.search(item)
        self.click_at(1294, 290, delay=1)

        if amount < 50:
            for _ in range(amount):
                self.press("e")
                self.sleep(0.3)
            return

        for _ in range(math.ceil(amount / 100)):
            self.press("a")
            self.sleep(0.5)

    def get_slots(self) -> int:
        """Attempts to OCR the amount of slots occupied in the structure.
        Returns the OCR'd amount as an integer, otherwise -1 on failure.
        """
        if not self.is_open():
            raise InventoryNotOpenError

        slots = self.window.grab_screen((1090, 503, 31, 15))
        masked = self.window.denoise_text(
            slots, (251, 227, 124), variance=27, dilate=False
        )
        result: str = tes.image_to_string(
            masked, config="-c tessedit_char_whitelist=0123456789lIWVSi --psm 10 -l eng"
        ).rstrip()
        if not result:
            return -1
        to_replace = {
            "/": "7",
            "l": "1",
            "I": "1",
            "W": "11",
            "V": "1",
            "i": "1",
            "S": "5",
        }
        for k, v in to_replace.items():
            result = result.replace(k, v)

        # replace mistaken "0"s, strip off newlines
        return int(result.replace("O", "0")) or -1

    def is_full(self) -> bool:
        """Checks if the vault is full, raises an `AttributeError` if no
        max slot image path was defined."""
        if self._capacity is None:
            raise AttributeError(
                f"Unabled to check slots, missing 'capacity' for '{self._name}'"
            )
        if not self.is_open():
            raise InventoryNotOpenError

        if isinstance(self._capacity, str):
            return (
                self.window.locate_template(
                    self._capacity, region=self._SLOTS_REGION, confidence=0.9
                )
                is not None
            )
        return self._capacity - 5 <= self.get_slots() <= self._capacity

    def received_item(self) -> bool:
        """Checks if an item was added by matching for the added template"""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/added.png",
                region=self._ADDED_REGION,
                confidence=0.7,
            )
            is not None
        )

    def delete_search(self) -> None:
        """Deletes the last term in the searchbar by selecting all of it,
        deleting it with backspace and then escaping out."""
        if not self.is_open():
            raise InventoryNotOpenError

        self._click_searchbar(delete_prior=True)
        self.press("backspace")
        self.press("esc")

    def transfer_top_row(self, speed: int | float = 0.2) -> None:
        if not self.is_open():
            raise InventoryNotOpenError

        for idx, slot in enumerate(self.SLOTS, start=1):
            pg.moveTo(get_center(slot))
            self.press(self.keybinds.transfer)
            self.sleep(speed)

            if idx >= 6:
                return

    def get_amount_transferred(
        self, item: Item, mode: Literal["rm", "add"] = "rm"
    ) -> int:
        """OCRs the amount transferred into the inventory by checking for the
        amount on the lefthand side of the screen."""
        # prepare the image
        for _ in range(10):
            roi = self._get_transferred_frame(item, mode)
            if roi:
                break
            self.sleep(0.1)

        if not roi:
            return 0

        img = self.window.grab_screen(roi, convert=False)
        img = self.window.denoise_text(
            img, denoise_rgb=(255, 255, 255), variance=10, upscale=True, upscale_by=3
        )
        # get the raw tesseract result
        raw_result: str = tes.image_to_string(
            img,
            config="-c tessedit_char_whitelist='0123456789liIxObL ' --psm 7 -l eng",
        )
        try:
            # replace all the mistaken "1"s
            for char in ["I", "l", "i", "b", "L"]:
                raw_result = raw_result.replace(char, "1")

            # replace mistaken "0"s, strip off newlines
            filtered = raw_result.replace("O", "0").replace("~", "x").rstrip()

            # find the x to slice out the actual number
            x = filtered.find("x")
            if x == -1 or not filtered or filtered == "x":
                return 0
            return int(filtered[:x])
        except:
            return 0

    def _get_transferred_frame(
        self, item: Item, mode: Literal["rm", "add"] = "rm"
    ) -> tuple[int, int, int, int] | None:
        if not item.added_icon:
            raise AttributeError("Cant find transferred frame without 'added_icon'")

        icon_pos = self.window.locate_template(
            item.added_icon, region=(0, 970, 160, 350), confidence=0.7
        )
        if icon_pos is None:
            return None

        # get our region of interest
        text_start_x = icon_pos[0] + icon_pos[2]

        if mode == "rm":
            text_end = text_start_x + self.window.convert_width(130), icon_pos[1]
        else:
            text_end = text_start_x + self.window.convert_width(95), icon_pos[1]

        roi = (
            *text_end,
            self.window.convert_width(290),
            self.window.convert_height(25),
        )

        if item.added_text is None:
            raise AttributeError(f"You did not define an 'added_text' for {item}!")

        # find the items name to crop out the numbers
        name_text = self.window.locate_template(
            item.added_text, region=roi, confidence=0.7, convert=False
        )
        if name_text is None:
            return None

        # get our region of interest (from end of "Removed:" to start of "Item")
        return (
            *text_end,
            self.window.convert_width(int(name_text[0] - text_end[0])),
            self.window.convert_height(25),
        )

    def _await_receiving_remove_inventory(self) -> None:
        """Waits until 'Receiving Remote Inventory' disappears.

        Raises:
        ------------
        `ReceivingRemoveInventoryTimeout` if it did not disappear after 30
        seconds, usually indicating a server crash.
        """
        c = 0
        while self._receiving_remote_inventory():
            self.sleep(0.1)
            c += 1
            if c > 300:
                raise ReceivingRemoveInventoryTimeout(self)

    def _click_searchbar(self, delete_prior: bool = True) -> None:
        """Clicks into the searchbar"""
        self.click_at(self._SEARCHBAR)
        if not delete_prior:
            return

        with pg.hold("ctrl"):
            self.sleep(0.1)
            pg.press("a")
            self.sleep(0.1)

    def _receiving_remote_inventory(self) -> bool:
        """Checks if the 'Receiving Remote Inventory' text is visible."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/remote_inventory.png",
                region=self._REMOTE_INVENTORY,
                confidence=0.8,
            )
            is not None
        )

    def _has_engram(self, item: Item) -> bool:
        """Checks if the given item can be crafted."""
        if self._craftables is None:
            raise AttributeError("Unexpected call, `craftables` is `None`.")

        if item not in self._craftables:
            raise ValueError(f"'{item.name}' is not part of '{self._name}' craftables!")

        self.search(item)
        self.sleep(0.5)
        return (
            self.window.locate_template(
                item.inventory_icon, self._ITEM_REGION, confidence=0.8
            )
            is not None
        )

    def _receive_stack(self, item: Item, before: int) -> None:
        start = time.time()

        while self.count(item) == before:
            self.sleep(0.05)
            if timedout(start, 5):
                raise NoItemsAddedError(item.name)

        print(f"Receiving stack took {time.time() - start}")
