import time
from typing import Iterable, Literal, Optional, overload

import pyautogui as pg  # type: ignore[import]
import pydirectinput as input  # type: ignore[import]

from ..._ark import Ark
from ..._tools import timedout
from ...buffs import BROKEN_BONES, HUNGRY, THIRSTY, Buff
from ...exceptions import PlayerDidntTravelError, PlayerDiedError
from ...interfaces.hud_info import HUDInfo
from ...interfaces.inventories import PlayerInventory
from ...interfaces.structures.structure import Structure
from ...items import Item
from .._stats import Stats

class Player(Ark):
    """Represents the player in ark.

    Provides the ability to control the player to emulate actions a real player
    could do, such as turning or walking, checking on the buffs / debuffs or health,
    and using the hotbar.

    Additionally, it providdes a dedicated `PlayeInventory` which can be accessed
    through the players `inventory` attribute.

    Attributes
    ----------
    inventory :class:`PlayerInventory`:
        The players inventory

    hotbar :class:`list[str]`:
        The players hotbar slots
    """
    _DEBUFF_REGION = (1270, 950, 610, 130)
    _ADDED_REGION = (0, 450, 314, 240)
    _HP_BAR = (1882, 1022, 15, 50)
    _HAS_DIED = (630, 10, 590, 80)
    _STAM_BAR = (1850, 955, 70, 65)
    
    @overload
    def __init__(self, *, stats: Stats) -> None:
        ...

    @overload
    def __init__(self, health: int, food: int, water: int, weight: int) -> None:
        ...

    def __init__(
        self, health=None, food=None, water=None, weight=None, *, stats=None
    ) -> None:
        super().__init__()
        self.inventory = PlayerInventory()
        if stats is not None:
            self.stats = stats
        else:
            self.stats = Stats(health, food, water, weight)
        self.HOTBAR = [
            self.keybinds.hotbar_1,
            self.keybinds.hotbar_2,
            self.keybinds.hotbar_3,
            self.keybinds.hotbar_4,
            self.keybinds.hotbar_5,
            self.keybinds.hotbar_6,
            self.keybinds.hotbar_7,
            self.keybinds.hotbar_8,
            self.keybinds.hotbar_9,
            self.keybinds.hotbar_0,
        ]
        self.hud = HUDInfo()
        self._lr_factor = 3.2 / self.settings.left_right_sens
        self._ud_factor = 3.2 / self.settings.up_down_sens
        self._fov_factor = 1.25 / self.settings.fov_multiplier

    def turn_90_degrees(
        self, direction: Literal["right", "left"] = "right", delay: int | float = 0
    ) -> None:
        """Turns by 90 degrees in given direction"""
        val = 129 if direction == "right" else -129
        self.turn_x_by(val)
        self.sleep(delay)

    def look_down_hard(self) -> None:
        """Looks down all the way to the ground"""
        for _ in range(7):
            self.turn_y_by(50, delay=0.05)
        self.sleep(0.3)

    def look_up_hard(self) -> None:
        """Looks up all the way to the ceiling"""
        for _ in range(7):
            self.turn_y_by(-50, delay=0.05)
        self.sleep(0.3)

    def turn_y_by(self, amount: int, delay: int | float = 0.1) -> None:
        """Turns the players' y-axis by the given amount"""
        input.moveRel(
            0,
            round(amount * self._ud_factor * self._fov_factor),
            0,
            None,
            False,
            False,
            True,
        )
        self.sleep(delay)

    def turn_x_by(self, amount: int, delay: int | float = 0.1) -> None:
        """Turns the players' x-axis by the given amount"""
        input.moveRel(
            round(amount * self._lr_factor * self._fov_factor),
            0,
            0,
            None,
            False,
            False,
            True,
        )
        self.sleep(delay)

    def pick_up(self) -> None:
        """Picks up an item by pressing E"""
        self.press(self.keybinds.use)

    def pick_all(self) -> None:
        """Picks all items by pressing F"""
        self.press(self.keybinds.target_inventory)

    def drop_all(self, items: Optional[Iterable[Item | str]] = None) -> None:
        """Opens the inventory and drops all on the specified item"""
        self.inventory.open()
        self.inventory.drop_all(items)
        self.inventory.close()

    def spam_hotbar(self):
        """Typewrites all the hotbar keys with crystals on them to open crystals fast."""
        pg.typewrite("".join(c for c in self.HOTBAR), interval=0.01)

    def set_hotbar(self) -> None:
        """Sets the hotbar using shift left click on the crystals"""
        input.keyDown("shift")
        for _ in range(4):
            for slot in self.HOTBAR:
                self.press(slot)
                self.sleep(0.5)
        input.keyUp("shift")

    def walk(self, key, duration):
        """'Walks' the given direction for the given duration.

        Parameters:
        ----------
        key :class:`str`:
            The key to hold to walk

        duration :class: `int`|`float`:
            The duration to walk for
        """
        input.keyDown(key)
        self.sleep(duration=duration)
        input.keyUp(key)

    def crouch(self) -> None:
        """Crouches the player"""
        self.press(self.keybinds.crouch)

    def prone(self) -> None:
        """Prones the player"""
        self.press(self.keybinds.prone)

    def stand_up(self) -> None:
        for _ in range(3):
            input.press("shift")
        input.keyUp("shift")
    def disable_hud(self) -> None:
        """Disables HUD"""
        self.press("backspace")

    def pick_up_bag(self):
        """Picks up items from a drop script bag, deletes the bag after."""
        self.look_down_hard()
        self.press(self.keybinds.target_inventory)
        self.sleep(0.5)
        self._popcorn_bag()

    def set_first_person(self) -> None:
        """Sets the player to first person"""
        self.mouse_scroll(1)

    def hide_hands(self) -> None:
        """Looks up and down to hide the hands temporarily"""
        self.look_up_hard()
        self.sleep(0.2)
        self.look_down_hard()
        self.disable_hud()
        self.sleep(0.5)
        self.turn_y_by(-160)
        self.sleep(0.3)

    def received_item(self) -> bool:
        """Returns whether the player has received an item. Not to be confused
        with the `received_item` method of the `Inventory` class, which does
        the same but on a different position."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/added.png",
                region=self._ADDED_REGION,
                confidence=0.75,
            )
            is not None
        )

    def has_died(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/you_died.png",
                region=self._HAS_DIED,
                confidence=0.7,
            )
            is not None
        )

    def is_spawned(self) -> bool:
        """Checks if the player is spawned"""
        return self.hud.is_open()

    def has_buff(self, buff: Buff) -> bool:
        """Checks if the player has the given buff"""
        return (
            self.window.locate_template(
                buff.image, region=self._DEBUFF_REGION, confidence=0.8
            )
            is not None
        )

    def needs_recovery(self) -> bool:
        """Checks if the player needs to recover"""
        return any(self.has_buff(buff) for buff in [THIRSTY, HUNGRY, BROKEN_BONES])

    def do_drop_script(self, item: Item, target: Structure):
        """Does the item drop script for the given item in the given structure.
        Used to empty heavy items out of structures that are not dedis. Player
        has to be non crouching and will end up as not crouching.

        Parameters:
        -----------
        item :class:`Item`:
            The item to dropscript for

        target :class:`Inventory`:
            The inventory to take the item out of.

        slot :class: `int`:
            The slot to take the item from, required if the inventory has
            an item folder in slot 1.
        """
        self.crouch()
        self.sleep(0.5)
        target.open()

        target.inventory.take(item, amount=1)
        self.inventory.await_items_added(item)
        self.sleep(0.3)

        self.inventory.drop_all([item])
        self.inventory.search(item)

        while target.inventory.has(item, is_searched=True):
            target.inventory.transfer_all()
            target.inventory.search(item)
            self.sleep(0.2)

            if not target.inventory.has(item, is_searched=True):
                break

            self.inventory.drop(item, search=False)

            target.inventory.search(item)

        self.inventory.close()
        self.pick_up_bag()
        self.sleep(1)
        self.stand_up()

    def spawn_in(self) -> None:
        """Waits for the player to spawn in, catching possible scenarios such
        as the player dying instantly upon spawning.

        Parameters
        ---------
        screen :class:`SpawnScreen`:
            The spawn screen used to travel
        """
        start = time.time()
        while not self.is_spawned():
            pg.keyUp(self.keybinds.hud_info)
            pg.keyDown(self.keybinds.hud_info)
            self.sleep(0.1)

            if timedout(start, 60):
                pg.keyUp(self.keybinds.hud_info)
                raise PlayerDidntTravelError("Failed to spawn in!")

            if self.has_died():
                raise PlayerDiedError("Spawning")

        pg.keyUp(self.keybinds.hud_info)

    def _is_travelling(self) -> bool:
        """Check if we are currently travelling (whitescreen)"""
        return pg.pixelMatchesColor(
            *self.window.convert_point(959, 493), (255, 255, 255), tolerance=10
        )

    def _popcorn_bag(self) -> None:
        bag = Structure("Item Cache", "assets/wheels/item_cache.png")
        bag.open()
        bag.inventory.select_slot(0)

        while bag.inventory.is_open():
            self.press("o")
            self.sleep(0.3)
