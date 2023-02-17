from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import dacite

from ..config import ARK_PATH

@dataclass
class UserSettings:
    """Represents the GameUserSettings.ini"""

    path: Path = field(init=False)
    ui_scaling: float
    fov_multiplier: float
    left_right_sens: float
    up_down_sens: float
    hide_item_names: bool
    show_item_tooltips: bool
    auto_chatbox: bool
    toggle_hud: bool
    menu_transitions: bool
    resolution_x: int
    resolution_y: int
    server_filter: int
    last_server: str
    reverse_logs: bool

    @staticmethod
    def load(path: Optional[str] = None) -> UserSettings:
        """Loads the settings from GameUserSettings.ini, using the `ARK_PATH`
        provided in the configs or an alternatively passed path."""
        if path is None:
            path = f"{ARK_PATH}\Saved\Config\WindowsNoEditor\GameUserSettings.ini"

        with open(path) as f:
            contents = f.readlines()

        settings: dict[str, float | bool | str | Path] = {}
        settings["path"] = Path(path)

        # keep track of the session occurrences so we can find the last joined
        # server for the selected category, which is stored as an integer from 0-7
        session_occurences = 0
        for line in contents:
            if line.startswith("[ScalabilityGroups]"):
                break

            if "=" not in line:
                continue

            if "LastJoinedSessionPerCategory" in line and not settings.get("last_server"):
                if session_occurences == settings.get("server_filter"):
                    settings["last_server"] = line.split("=")[1].strip()
                    continue

            option, value = line.rstrip().split("=")
            setting = _KEY_MAP.get(option)

            if setting is not None:
                settings[setting] = _set_type(value)  # type: ignore[assignment]

        return dacite.from_dict(UserSettings, settings)

    @property
    def last_modified(self) -> str:
        epoch = self.path.stat().st_mtime
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def listen_for_change(self) -> None:
        """Listens to any changes made to the file, this is done by loading the
        data of the last modified timestamp, and then waiting for the timestamp
        to change. Once it has we compare the new data to the previous data and
        notify about any changes.
        
        Particularly useful to find the name of a setting in the .ini by just
        changing it ingame, listening to the changes and see what value gets
        changed."""
        last_change = self.last_modified
        with open(self.path) as f:
            old_data = f.readlines()

        while self.last_modified == last_change:
            pass

        print("Change detected in GameUserSettings.ini!")
        while True:
            try:
                with open(self.path) as f:
                    new_data = f.readlines()
            except PermissionError:
                continue
            else:
                break

        for old_line, new_line in zip(old_data, new_data):
            if old_line != new_line:
                print(f"Setting '{old_line.strip()}' changed to '{new_line.strip()}'!")


_KEY_MAP = {
    "UIScaling": "ui_scaling",
    "FOVMultiplier": "fov_multiplier",
    "LookLeftRightSensitivity": "left_right_sens",
    "LookUpDownSensitivity": "up_down_sens",
    "HideItemTextOverlay": "hide_item_names",
    "bEnableInventoryItemTooltips": "show_item_tooltips",
    "bShowChatBox": "auto_chatbox",
    "bToggleExtendedHUDInfo": "toggle_hud",
    "bDisableMenuTransitions": "menu_transitions",
    "ResolutionSizeX": "resolution_x",
    "ResolutionSizeY": "resolution_y",
    "LastServerSearchType": "server_filter",
    "bReverseTribeLogOrder": "reverse_logs"
}


def _set_type(val: str) -> str | bool | float | int:
    """Sets the value from the .ini to the correct type"""
    if val == "True":
        return True

    elif val == "False":
        return False
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        return val
