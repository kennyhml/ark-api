import time
from typing import final

from ... import config
from ..._helpers import timedout
from ...entities.player import Player
from ..spawn_screen import SpawnScreen
from ..wheels import TekPodWheel
from .structure import Structure


@final
class TekSleepingPod(Structure):
    """Represents the Tek Sleeping Pod in Ark.
    
    Provides ability to enter the pod to heal the player and access
    to the `TekPodWheel` class.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name, TekPodWheel())
        self.action_wheel: TekPodWheel
        self.interface = SpawnScreen()
        
    def spawn(self) -> None:
        self.interface.travel_to(self.name)

    def heal(self, player: Player) -> None:
        """Heals the player until either all relevant stats are full,
        or the calculated duration has expired."""
        player.stand_up()
        player.look_down_hard()

        self.action_wheel.activate()
        self.action_wheel.lay_on()

        player.inventory.open()
        self._wait_to_heal(player)
        player.inventory.close()

    def _wait_to_heal(self, player: Player) -> None:
        """Waits to heal the player given its stats or the state
        of the stats."""
        hp_duration = player.stats.health / 10
        water_duration = player.stats.water / 2.5
        food_duration = player.stats.food / 2.5

        max_duration = max(hp_duration, water_duration, food_duration) * config.TIMER_FACTOR
        start = time.time()
        while not all(
            (
                player.inventory.hp_full(),
                player.inventory.water_full(),
                player.inventory.food_full(),
            )
        ):
            self.sleep(1)
            if timedout(start, max_duration):
                break

    def leave(self) -> None:
        """Leaves the tek pod"""
        self.press(self.keybinds.use)