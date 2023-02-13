
from .structure import Structure


class Grinder(Structure):
    """Represents the grinder inventory in ark.

    Is able to be turned on and off and grind all.
    """

    GRIND_ALL_BUTTON = (740, 570, 444, 140)


    def __init__(self) -> None:
        super().__init__("Grinder", "grinder")

    def grind_all(self) -> bool:
        """Presses the grind all button if it is available.
        Returns whether items got grinded or not.
        """
        if not self.can_grind():
            return False

        self.click_at(969, 663, delay=0.3)
        return True

    def can_grind(self) -> bool:
        """Checks if the grinder can grind"""
        return (
            self.window.locate_template(
                "templates/grind_all_items.png",
                region=self.GRIND_ALL_BUTTON,
                confidence=0.85,
            )
            is not None
        )