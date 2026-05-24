from typing import final
from .structure import Structure
from .._button import Button
from enum import Enum
from ...exceptions import InterfaceError
import time
from ..._helpers import timedout


class CryobreederState(str, Enum):
    UNPREPARED = "unprepared"
    READY_TO_BREED = "ready_to_breed"
    BREEDING = "breeding"
    UNKNOWN = "unknown"


@final
class CryoBreeder(Structure):

    BREED_BUTTON = Button((955, 620), (807, 606, 306, 33))
    START_BREEDING_BUTTON = Button((1210, 753), (1064, 739, 310, 30))

    def __init__(self) -> None:
        super().__init__(
            name="Cryo Breeder",
            action_wheel="assets/wheels/industrial_grinder.png",
        )

    @property
    def state(self) -> CryobreederState:
        if (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/prepare_dinos.png",
                self.BREED_BUTTON.region,
                0.8,
            )
            is not None
        ):
            return CryobreederState.UNPREPARED
        if (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/start_breeding.png",
                self.BREED_BUTTON.region,
                0.8,
            )
            is not None
        ):
            return CryobreederState.READY_TO_BREED
        if (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/view_breeding_progress.png",
                self.BREED_BUTTON.region,
                0.8,
            )
            is not None
        ):
            return CryobreederState.BREEDING
        return CryobreederState.UNKNOWN

    def start_breed(self) -> None:
        start = time.time()
        if self.state not in (
            CryobreederState.UNPREPARED,
            CryobreederState.READY_TO_BREED,
        ):
            raise InterfaceError("Cryobreeder is not ready")

        last_click = None
        while self.state != CryobreederState.READY_TO_BREED:
            if timedout(start, 90):
                raise

            if last_click is None or timedout(last_click, 5):
                self.click_at(self.BREED_BUTTON.location)
                last_click = time.time()
            time.sleep(0.1)

        last_click = None
        while self.state != CryobreederState.BREEDING:
            if timedout(start, 90):
                raise

            if last_click is None or timedout(last_click, 3):
                self.click_at(self.BREED_BUTTON.location)
                time.sleep(0.5)
                self.click_at(self.START_BREEDING_BUTTON.location)
                last_click = time.time()
            time.sleep(0.1)
