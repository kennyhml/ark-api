import pyautogui as pg  # type: ignore[import]

from ark.exceptions import ServerNotFoundError
from ark.server.server import Server

from .._ark import Ark


class SessionList(Ark):
    """Represents the main menu Session List in Ark.

    Provides the ability to rejoin a specific server.
    """

    _FILTERS = {"Official Servers": (369, 863), "Favorites": (373, 925)}
    _SESSION_LIST_REGION = (110, 100, 230, 80)
    _TOP_SERVER_REGION = (90, 200, 430, 90)
    _JOINING_FAILED = (712, 354, 486, 76)

    def refresh(self) -> None:
        """Clicks the refresh button"""
        self.click_at(1229, 941, delay=0.5)

    def join_server(self) -> None:
        self.click_at(990, 943, delay=0.5)

    def open(self) -> None:
        while not self.is_open():
            self.click_at(117, 528, delay=0.5)
            self.sleep(2)

    def connect(self, server: Server) -> None:
        """Joins the given server by the servers search name attribute.

        Parameters:
        ----------
        server :class:`Server`:
            The server to join as a Server object.
        """
        try:
            self.search_server(server)
        except ServerNotFoundError:
            print("Failed to find the server after 15min!")

        while self.is_open():
            self.join_server()
            self.sleep(45)

            if not self._server_is_ghosting():
                continue

            self.sleep(300)
            self.connect(server)

    def search_server(self, server: Server) -> None:
        """Searches for the given server, waits for it to pop up.

        Parameters:
        ----------
        server :class:`Server`:
            The server to search for as a Server object.
        """
        self.click_at(616, 143, delay=0.5)
        with pg.hold("ctrl"):
            pg.press("a")
            pg.press("backspace")

        pg.typewrite(server.name, interval=0.01)
        self.press("enter")
        self.sleep(5)

        # attempt to find the server up to 30 times, waiting 30 seconds each time.
        # after each 30 seconds the session list is refreshed
        attempts = 0
        for _ in range(30):
            count = 0
            while not self.server_found():
                self.sleep(1)
                count += 1

                if count > 30:
                    attempts += 1
                    self.refresh()
                    break
            else:
                self.click_at(959, 237, delay=0.5)
                return

        raise ServerNotFoundError(f"Failed to find {server.name}!")

    def is_open(self) -> bool:
        """Checks if the session list menu is open"""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/session_list.png",
                region=self._SESSION_LIST_REGION,
                confidence=0.8,
            )
            is not None
        )

    def server_found(self) -> bool:
        """Checks if the favorited server has been found"""
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/server_favorite.png",
                region=self._TOP_SERVER_REGION,
                confidence=0.75,
            )
            is not None
        )

    def _server_is_ghosting(self) -> bool:
        return (
            self.window.locate_template(
                f"{self.PKG_DIR}/assets/interfaces/joining_failed.png",
                region=self._JOINING_FAILED,
                confidence=0.7,
            )
            is not None
        )
