"""
Ark API module representing the player in ark.
"""
import time
from typing import Iterable, Literal, Optional

import pyautogui as pg  # type: ignore[import]
import pydirectinput as input  # type: ignore[import]
from numpy import isposinf

from .._ark import Ark
from .._tools import timedout
from ..buffs import BROKEN_BONES, HUNGRY, THIRSTY, Buff
from ..exceptions import InventoryNotAccessibleError, PlayerDidntTravelError
from ..interfaces import Inventory, PlayerInventory, Structure
from ..items import Y_TRAP, Item


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
    _HP_BAR = (1882, 1022, 15, 50)
    _HAS_DIED = (630, 10, 590, 80)
    _STAM_BAR = (1850, 955, 70, 65)
    _DAY_REGION = (0, 10, 214, 95)

    def __init__(
        self,
        health: int,
        food: int,
        water: int,
        weight: int,
        melee: int,
        crafting: int,
        fortitude: int,
    ) -> None:
        super().__init__()
        self.inventory = PlayerInventory()
        self.HOTBAR = [
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

    def turn_90_degrees(
        self, direction: Literal["right", "left"] = "right", delay: int | float = 0
    ) -> None:
        """Turns by 90 degrees in given direction"""
        val = 130 if direction == "right" else -130
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
        input.moveRel(0, amount, 0, None, False, False, True)
        self.sleep(delay)

    def turn_x_by(self, amount: int, delay: int | float = 0.1) -> None:
        """Turns the players' x-axis by the given amount"""
        input.moveRel(amount, 0, 0, None, False, False, True)
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
        self.press("shift")

    def disable_hud(self) -> None:
        """Disables HUD"""
        self.press("backspace")

    def pick_up_bag(self):
        """Picks up items from a drop script bag, deletes the bag after."""
        self.look_down_hard()
        self.press(self.keybinds.target_inventory)
        self.sleep(0.5)
        self._popcorn_bag()

    def travel(self) -> None:
        """Waits for the loading screen to appear, then to spawn in.
        Being spawned in is determined by the orange "Day" of the HUD.

        """
        start = time.time()

        while not self._is_travelling():
            self.sleep(0.1)
            if timedout(start, 45):
                raise PlayerDidntTravelError
        self.sleep(3)

        self._spawn_in()

    def set_first_person(self) -> None:
        """Sets the player to first person"""
        self.mouse_scroll(1)

    def has_died(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/you_died.png",
                region=self._HAS_DIED,
                confidence=0.7,
            )
            is not None
        )

    def hide_hands(self) -> None:
        """Looks up and down to hide the hands temporarily"""
        self.look_up_hard()
        self.sleep(0.2)
        self.look_down_hard()
        self.disable_hud()
        self.sleep(0.5)
        self.turn_y_by(-160)
        self.sleep(0.3)

    def is_spawned(self) -> bool:
        """Checks if the player is spawned"""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/day.png",
                region=self._DAY_REGION,
                confidence=0.8,
                grayscale=True,
            )
            is not None
        )

    def needs_recovery(self) -> bool:
        """Checks if the player needs to recover"""
        return any(self.has_effect(buff) for buff in [THIRSTY, HUNGRY, BROKEN_BONES])

    def has_effect(self, buff: Buff) -> bool:
        """Checks if the player has the given buff"""
        return (
            self.window.locate_template(
                buff.image, region=self._DEBUFF_REGION, confidence=0.8
            )
            is not None
        )

    def _spawn_in(self) -> None:
        """Waits for the player to spawn in, up to 50 seconds after which a
        `PlayerDidntTravelError` is raised."""
        start = time.time()
        while not (self.is_spawned() or self.has_died()):
            pg.keyUp(self.keybinds.toggle_hud)
            pg.keyDown(self.keybinds.toggle_hud)
            self.sleep(0.1)

            if timedout(start, 60):
                pg.keyUp(self.keybinds.toggle_hud)
                raise PlayerDidntTravelError("Failed to spawn in!")

        pg.keyUp(self.keybinds.toggle_hud)

    def _is_travelling(self) -> bool:
        """Check if we are currently travelling (whitescreen)"""
        return pg.pixelMatchesColor(
            *self.window.convert_point(959, 493), (255, 255, 255), tolerance=10
        )

    def do_crop_plots(self, refill_pellets: bool = False) -> None:
        """Empties all stacks of crop plots, starts facing the gacha,
        ends facing the gacha."""
        self.sleep(0.5)
        self.press(self.keybinds.crouch)

        for _ in range(3):
            self.turn_90_degrees()
            self.do_crop_plot_stack(refill_pellets)
        self.turn_90_degrees()
        self.sleep(0.2)

    def name_crop_plots(self) -> None:
        """Names the crop plots for you!"""
        self.sleep(0.5)
        for _ in range(3):
            self.turn_90_degrees()
            self.name_crop_plot_stack()

    def do_precise_crop_plots(
        self, item: Item, refill_pellets: bool = False, precise: bool = True
    ) -> None:
        """Does the crop plot stack, used to always do them precisely, now the
        flag can be changed, should probably rename the method and remove the
        old one.

        Parameters:
        ------------
        item :class:`Item`:
            The item to take out of the crop plots

        refill_pellets :class:`bool`:
            Whether to put pellets in or not

        precise :class:`bool`:
            Whether to aim for 100% access rate using folders
        """
        self.sleep(0.5)
        for _ in range(3):
            self.turn_90_degrees()
            self.do_precise_crop_plot_stack(item, refill_pellets, precise=False)
        self.turn_90_degrees()
        self.sleep(0.2)

    def adjust_for_crop_plot(self, crop_plot: Structure, expected_index: int) -> None:
        """Checks if the expected crop plot was opened, adjusts if it was not.

        Parameters:
        -----------
        crop_plot :class:`Structure`:
            The crop plot we are trying to open

        expected_index :class:`int`:
            The expected index of the crop plot (in the stack)

        TODO: Raise an error when the correct crop plot could not be opened whatsoever
        """
        index = crop_plot.inventory.get_stack_index()
        while index != expected_index:
            # no index at all was found, try to reopen the crop plot
            if not index:
                crop_plot.inventory.close()
                crop_plot.inventory.open()
                index = crop_plot.inventory.get_stack_index()
                continue
            crop_plot.inventory.close()

            # check if we need to correct higher or lower
            if index > expected_index:
                self.turn_y_by(7)
            else:
                self.turn_y_by(-6)

            # recheck the index
            crop_plot.inventory.open()
            index = crop_plot.inventory.get_stack_index()

    def take_item_put_pellets(
        self, crop_plot: Structure, refill_pellets: bool, item: Optional[Item] = None
    ) -> None:
        """Opens the crop plot and takes either the specified item, or takes all.
        Refills the pellets if passed.
        """
        crop_plot.inventory.open()
        if item and crop_plot.inventory.has_item(item):
            crop_plot.inventory.take_all_items(item)

        elif not item:
            crop_plot.inventory.click_transfer_all()

        if refill_pellets:
            self.inventory.transfer_all(crop_plot.inventory)

        crop_plot.inventory.close()

    def do_crop_plot_stack(self, refill_pellets: bool = False) -> None:
        """Empties the current stack of crop plots.

        Takes all traps from the crop plots using the searchbar, then transfers
        all to put pellets in. If no traps are in the crop plot, taking traps
        will be skipped.

        Parameters:
        -----------
        refill_pellets :class:`bool`:
            Whether pellets need to be refilled or not
        """
        crop_plot = Structure("Tek Crop Plot", "tek_crop_plot")

        # look down to sync
        self.look_down_hard()
        self.sleep(0.1)

        for val in [-130, *[-17] * 5]:
            self.turn_y_by(val)
            self.sleep(0.3)
            self.take_item_put_pellets(crop_plot, refill_pellets, Y_TRAP)

        # stand up and take the current one
        self.press(self.keybinds.crouch)
        for val in [50, -17, -17]:
            self.turn_y_by(val)
            self.take_item_put_pellets(crop_plot, refill_pellets, Y_TRAP)

        # back to crouching
        self.press(self.keybinds.crouch)

    def do_precise_crop_plot_stack(
        self,
        item: Optional[Item] = None,
        refill_pellets: bool = False,
        max_index: int = 8,
        precise: bool = True,
    ) -> None:
        """Empties the current stack of crop plot, but aims for a 100% access rate.

        This is achieved by adding a folder to each crop plot from bottom to top,
        AAA to HHH, so the bot can see the folder and know which crop plot
        it accessed thus being able to adjust itself higher or lower.

        Parameters:
        -----------

        item :class:`Item`:
            The item to take out of the crop plot, as `Item` object.

        take_all :class:`bool`:
            Whether the bot should take all from the crop plot

        max_index :class:`int`:
            The highest crop plot to be accessed, default 8
        """
        crop_plot = Structure("Tek Crop Plot", "tek_crop_plot")
        self.crouch()
        turns = [-130, -20, -20, -17, -15, 35, -17, -17, -15, -10, -20]
        self.look_down_hard()
        self.sleep(0.1)

        # go through each turn attempting to access the respective
        for expected_index, turn in enumerate(turns, start=1):
            if expected_index - 1 == max_index:
                return

            if expected_index == 6:
                self.crouch()

            self.turn_y_by(turn)
            self.sleep(0.3)
            try:
                # check for the correct crop plot
                crop_plot.inventory.open()
                if precise:
                    self.adjust_for_crop_plot(crop_plot, expected_index)

                # empty it
                self.take_item_put_pellets(crop_plot, refill_pellets, item)

            except InventoryNotAccessibleError as e:
                if expected_index < 3:
                    continue
                raise e

    def name_crop_plot_stack(self) -> None:
        """Names the crop plot stack to prepare the tower for 100% access running.
        Will not work properly if some crop plots already have folders, the most
        bottom crop plot needs to be on a highered ceiling.
        """
        folders = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]

        # get the most bottom crop plot and create the inital folder
        crop_plot = Structure("Tek Crop Plot", "tek_crop_plot")
        self.crouch()

        self.look_down_hard()
        self.sleep(0.1)
        self.turn_y_by(-130)
        self.sleep(0.3)

        crop_plot.inventory.open()
        crop_plot.inventory.create_folder("AAA")
        crop_plot.inventory.close()

        index = 1
        # go through each turn attempting to access the respective crop plot
        while index != 8:
            self.turn_y_by(-3)
            crop_plot.inventory.open()

            # there already is a folder
            if crop_plot.inventory.get_stack_index():
                crop_plot.inventory.close()
                self.sleep(0.2)
                continue

            # empty crop plot, create next folder in line
            crop_plot.inventory.create_folder(folders[index])
            crop_plot.inventory.close()
            index += 1

            # stand back up after "EEE"
            if index == 5:
                self.crouch()
                self.turn_y_by(60)
                self.sleep(0.5)

    def do_drop_script(self, item: Item, target_inventory: Inventory, slot=2):
        """Does the item drop script for the given item in the given structure.
        Used to empty heavy items out of structures that are not dedis. Player
        has to be non crouching and will end up as not crouching.

        Parameters:
        -----------
        item :class:`Item`:
            The item to dropscript for

        target_inventory :class:`Inventory`:
            The inventory to take the item out of.

        slot :class: `int`:
            The slot to take the item from, required if the inventory has
            an item folder in slot 1.
        """
        self.crouch()
        self.sleep(0.5)
        target_inventory.open()

        target_inventory.take_one_item(item, slot=slot)
        self.inventory.await_items_added()
        self.sleep(0.3)
        self.inventory.drop_all_items(item)

        self.inventory.search_for(item)

        while True:
            target_inventory.search_for(item)
            self.sleep(0.5)
            if not target_inventory.has_item(item):
                break

            target_inventory.click_transfer_all()
            self.sleep(0.3)
            self.popcorn_items(3)

        self.inventory.close()
        self.pick_up_bag()
        self.sleep(1)
        self.crouch()
        self.sleep(0.5)

    def item_added(self) -> bool:
        return (
            self.window.locate_template(
                "templates/added.png", region=(0, 450, 314, 240), confidence=0.75
            )
            is not None
        )

    def await_item_added(self) -> bool:
        c = 0
        while not self.item_added():
            self.sleep(0.1)
            c += 1
            if c > 10:
                return False
        return True

    def _popcorn_bag(self) -> None:
        bag = Structure("Item Cache", "assets/wheels/item_cache.png")
        bag.open()
        bag.inventory.select_slot(0)

        while bag.inventory.is_open():
            self.press("o")
            self.sleep(0.3)