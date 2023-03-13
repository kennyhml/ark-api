import inspect


class TerminatedError(Exception):
    """Raised when the bot has been termined by user or critical error"""


class WheelError(Exception):
    """Base class for all wheel exceptions"""


class WheelNotAccessibleError(WheelError):
    """Raised when a wheel accessed."""

    def __init__(self, wheel: str) -> None:
        self.wheel = wheel

    def __str__(self) -> str:
        return f"Wheel '{self.wheel}' could not be activated!"


class UnexpectedWheelError(WheelError):
    """Raised when a wheel was accessed, but not the correct one"""

    def __init__(self, expected: str, got: str) -> None:
        self.expected_wheel = expected
        self.got_wheel = got

    def __str__(self) -> str:
        return f"Unexpected wheel accessed. Expected '{self.expected_wheel}', got '{self.got_wheel}'!"


class ActionNotFoundError(WheelError):
    """Raised when a wheel action could not be found"""

    def __init__(self, action: str) -> None:
        self.action = action

    def __str__(self) -> str:
        return f"Failed to select action '{self.action}'!"


class InterfaceError(Exception):
    """Base class for all interface exceptions"""


class TimerNotVisibleError(InterfaceError):
    """Raised when the timer is not visible"""


class BedNotAccessibleError(InterfaceError):
    """Raised when the bed map could not be opened."""


class BedNotFoundError(InterfaceError):
    """Raised when the bed map could not be opened."""


class InventoryError(InterfaceError):
    """Base class for all inventory exceptions"""

    def __init__(self, inventory) -> None:
        self.inventory = inventory

    def __str__(self) -> str:
        return f"Ran into an inventory error at {self.inventory.name}"


class InventoryNotOpenError(InventoryError):
    """Raised when attempting an interaction within the
    inventory when it is not open"""

    def __init__(self) -> None:
        self.action = inspect.stack()[1][3]

    def __str__(self) -> str:
        return f"Attempted interaction '{self.action}' with closed inventory!"


class UnknownFolderIndexError(InventoryError):
    """Raised when a folder index is invalid or not determined"""

    def __str__(self) -> str:
        return f"Failed to find expected folder in {self.inventory.name}!"


class InventoryNotAccessibleError(InventoryError):
    """Raised when the inventory cannot be accessed."""

    def __str__(self) -> str:
        return f"Failed to access {self.inventory.name}!"


class InventoryNotClosableError(InventoryError):
    """Raised when the inventory cannot be closed"""

    def __str__(self) -> str:
        return f"Failed to close {self.inventory.name}!"


class ReceivingRemoveInventoryTimeout(InventoryError):
    """Raised when the 'Receiving Remote Inventory' text does not disappear."""

    def __str__(self) -> str:
        return f"Timed out receiving remote inventory at {self.inventory.name}!"


class NoItemsAddedError(InventoryError):
    """Raised when items were not added to the inventory if expected."""

    def __init__(self, expected_item: str) -> None:
        self.item = expected_item

    def __str__(self) -> str:
        return f"Expected item {self.item} was not added!"


class NoItemsDepositedError(InventoryError):
    """Raised when the 'X items deposited.' message does not appear."""

    def __str__(self) -> str:
        return f"Failed to deposit items into {self.inventory.name}"


class NoGasolineError(InventoryError):
    """Raised when a structure can not be turned on"""

    def __str__(self) -> str:
        return f"{self.inventory.name} is out of gasoline!"


class MissingItemErrror(InventoryError):
    """Raised when an item is missing"""

    def __init__(self, inventory, item: str) -> None:
        self.item = item
        self.inventory = inventory

    def __str__(self) -> str:
        return f"{self.item} could not be found in {self.inventory.name}!"


class PlayerError(Exception):
    """Base exception for all player errors"""


class PlayerDidntSpawnError(PlayerError):
    """Raised when the player could not spawn in"""


class PlayerDidntTravelError(PlayerError):
    """Raised when the travel screen could not be detected"""


class PlayerDiedError(PlayerError):
    """Raised when the player died"""

    def __init__(self, task: str) -> None:
        self.task = task

    def __str__(self) -> str:
        return f"Player died during task '{self.task}'!"


class LogsNotOpenedError(Exception):
    """Raised when the logs could not be opened"""


class ServerNotFoundError(Exception):
    """Raised when a server could not be found after 15 minutes."""


class DediNotInRangeError(Exception):
    """Raised when the dedi deposit text could not be detected"""


class DinoNotMountedError(Exception):
    """Raised when a dino cannot be mounted, either because it does not
    have a saddle, or because its not close enough."""
