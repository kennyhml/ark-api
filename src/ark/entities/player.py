"""
Ark API module representing the player in ark.
"""
from typing import Optional

import pyautogui as pg  # type: ignore[import]
import pydirectinput as input  # type: ignore[import]

from .._ark import Ark
from ..buffs import BROKEN_BONES, HUNGRY, THIRSTY, Buff
from ..exceptions import InventoryNotAccessibleError, PlayerDidntTravelError
from ..interfaces import Inventory, PlayerInventory
from ..items import Y_TRAP, Item
from ..structures import Structure


class Player(Ark):
    """Represents the player in ark.

    Provides the ability to control the player to do most actions
    a normal player could do. The inventory can be accessed through
    the players `inventory` attribute.

    Attributes
    ----------
    inventory :class:`PlayerInventory`:
        The players inventory

    hotbar :class:`list[str]`:
        The players hotbar slots
    """

    DEBUFF_REGION = (1270, 950, 610, 130)
    HP_BAR = (1882, 1022, 15, 50)

    def __init__(self) -> None:
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

    def set_first_person(self) -> None:
        """Sets the player to first person"""
        pg.scroll(100)

    def has_died(self) -> bool:
        return (
            self.window.locate_template(
                "ark/templates/you_died.png", region=(630, 10, 590, 80), confidence=0.7
            )
            is not None
        )

    def pick_up(self) -> None:
        """Picks up an item by pressing E"""
        self.press(self.keybinds.use)

    def pick_all(self) -> None:
        """Picks all items by pressing F"""
        self.press(self.keybinds.target_inventory)

    def empty_inventory(self) -> None:
        """Spams the hotbar and then drops all items in inventory to clear up
        the inventory. Spamming the hotbar is important in case it has somehow
        picked up a crystal, which goes into the hotbar.
        """
        self.spam_hotbar()
        self.inventory.open()
        self.inventory.click_drop_all()
        self.inventory.close()

    def drop_all_items(self, item: Item) -> None:
        """Opens the inventory and drops all on the specified item"""
        self.inventory.open()
        self.inventory.drop_all_items(item)
        self.inventory.close()

    def hide_hands(self) -> None:
        """Looks up and down to hide the hands temporarily"""
        self.look_up_hard()
        self.sleep(0.2)
        self.look_down_hard()
        self.disable_hud()
        self.sleep(0.5)
        self.turn_y_by(-160)
        self.sleep(0.3)

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

    def is_spawned(self) -> bool:
        """Checks if the player is spawned"""
        return (
            self.window.locate_template(
                "ark/templates/stamina.png", region=(1850, 955, 70, 65), confidence=0.65
            )
            is not None
        )

    def needs_recovery(self) -> bool:
        """Checks if the player needs to recover"""
        return any(self.has_effect(buff) for buff in [THIRSTY, HUNGRY, BROKEN_BONES])

    def has_effect(self, buff: Buff) -> bool:
        """Checks if the player has the given buff"""
        return (
            self.window.locate_template(buff.image, region=self.DEBUFF_REGION, confidence=0.8)
            is not None
        )

    def await_spawned(self) -> None:
        """Waits for the player to spawn in, up to 50 seconds after which a
        `PlayerDidntTravelError` is raised."""
        counter = 0
        while not (self.is_spawned() or self.has_died()):
            self.sleep(0.5)
            counter += 1

            if counter > 100:
                raise PlayerDidntTravelError("Failed to spawn in!")
        print("Now spawned!")
        self.sleep(1)

    def turn_90_degrees(self, direction: str = "right", delay: int | float = 0) -> None:
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
        """Crouches the player, or uncrouches if player is already crouched."""
        self.press(self.keybinds.crouch)

    def prone(self) -> None:
        """Prones the player, or unprones if the player is already proned"""
        self.press(self.keybinds.prone)

    def disable_hud(self) -> None:
        """Disables HUD"""
        self.press("backspace")

    def popcorn_bag(self) -> None:
        bag = Inventory("Bag", "bag")
        bag.open()
        self.move_to(1287, 289)
        while bag.is_open():
            self.press("o")
            self.sleep(0.3)

    def pick_up_bag(self):
        """Picks up items from a drop script bag, deletes the bag after."""
        self.look_down_hard()
        self.press(self.keybinds.target_inventory)
        self.sleep(0.5)
        self.popcorn_bag()

    def popcorn_items(self, iterations: int) -> None:
        for _ in range(iterations):
            for slot in [(168, 280), (258, 280), (348, 277)]:
                pg.moveTo(slot)
                pg.press(self.keybinds.drop)

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
                "ark/templates/added.png", region=(0, 450, 314, 240), confidence=0.75
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
