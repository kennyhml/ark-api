from .._ark import Ark


class MainMenu(Ark):
    """Represents the Main Menu in Ark.

    Provides the ability to recognize whether the player has disconnected.
    """

    _OPTIONS = (20, 600, 230, 76)
    _ACCEPT = (515, 320, 910, 390)

    def is_open(self) -> bool:
        """Returns whether the main menu is currently open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/main_menu_options.png",
                region=self._OPTIONS,
                confidence=0.8,
            )
            is not None
        )

    def player_disconnected(self) -> bool:
        """Returns whether the player was disconnected."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/main_menu_accept.png",
                region=self._ACCEPT,
                confidence=0.8,
            )
            is not None
        )
