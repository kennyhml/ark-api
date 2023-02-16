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

    @staticmethod
    def load(path: Optional[str] = None) -> UserSettings:
        if path is None:
            path = f"{ARK_PATH}\Saved\Config\WindowsNoEditor\GameUserSettings.ini"

        with open(path) as f:
            contents = f.readlines()

        settings: dict[str, float | bool | str | Path] = {}
        settings["path"] = Path(path)

        for line in contents:
            if line.startswith("[ScalabilityGroups]"):
                break

            if "=" not in line:
                continue

            option, value = line.rstrip().split("=")
            setting = config_map.get(option)

            if setting is not None:
                settings[setting] = _set_type(value)  # type: ignore[assignment]

        return dacite.from_dict(UserSettings, settings)

    @property
    def last_modified(self) -> str:
        epoch = self.path.stat().st_mtime
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def listen_for_change(self) -> None:
        last_change = self.last_modified
        with open(self.path) as f:
            old_data = f.readlines()

        while self.last_modified == last_change:
            pass

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


config_map = {
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
