from .._ark import Ark


class MainMenu(Ark):
    """Represents the ark main menu."""

    _OPTIONS = (20, 600, 230, 76)
    _ACCEPT = (515, 320, 910, 390)

    def is_open(self) -> bool:
        """Checks if the main menu is currently open."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/main_menu_options.png",
                region=self._OPTIONS,
                confidence=0.8,
            )
            is not None
        )

    def player_disconnected(self) -> bool:
        """Checks if the player was disconnected."""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/templates/main_menu_accept.png",
                region=self._ACCEPT,
                confidence=0.8,
            )
            is not None
        )
