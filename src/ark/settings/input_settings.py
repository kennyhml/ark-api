from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import dacite

from .. import config


@dataclass
class InputSettings:
    """Represents the Input.ini"""

    console: str
    crouch: str
    drop: str
    inventory: str
    prone: str
    target_inventory: str
    toggle_hud: str
    hud_info: str
    use: str
    logs: str
    transfer: str
    hotbar_0: str
    hotbar_1: str
    hotbar_2: str
    hotbar_3: str
    hotbar_4: str
    hotbar_5: str
    hotbar_6: str
    hotbar_7: str
    hotbar_8: str
    hotbar_9: str

    @staticmethod
    def load(path: Optional[str] = None) -> InputSettings:
        """Loads the settings from input.ini, using the `ARK_PATH` provided
        in the configs or an alternatively passed path."""
        if path is None:
            path = f"{config.ARK_PATH}\ShooterGame\Saved\Config\WindowsNoEditor\Input.ini"

        try:
            with open(path, encoding="utf-8") as f:
                contents = f.readlines()
        except UnicodeDecodeError:
            with open(path, encoding="utf-16") as f:
                contents = f.readlines()
           
        settings: dict[str, float | bool | str | Path] = {
            "console": "tab",
            "crouch": "c",
            "drop": "o",
            "inventory": "i",
            "prone": "x",
            "target_inventory": "f",
            "toggle_hud": "backspace",
            "hud_info": "h",
            "use": "e",
            "logs": "l",
            "transfer": "t",
            "hotbar_0": "0",
            "hotbar_1": "1",
            "hotbar_2": "2",
            "hotbar_3": "3",
            "hotbar_4": "4",
            "hotbar_5": "5",
            "hotbar_6": "6",
            "hotbar_7": "7",
            "hotbar_8": "8",
            "hotbar_9": "9",
        }

        settings["path"] = Path(path)
        for line in contents:
            if not "=" in line:
                continue

            if "ConsoleKeys" in line:
                action_name = "ConsoleKeys"
                key = line.split("=")[1].strip()
            else:
                pattern = r'ActionName="([^"]+)",Key=([^,]+)'
                matches = re.search(pattern, line)

                if matches is None:
                    continue

                action_name = matches.group(1)
                key = matches.group(2)

            action = _KEY_MAP.get(action_name)
            if key.lower() in _REPLACE and action is not None:
                settings[action] = str(_REPLACE.index(key.lower()))

            elif action is not None:
                settings[action] = key.lower()

        return dacite.from_dict(InputSettings, settings)


_KEY_MAP = {
    "ConsoleKeys": "console",
    "Crouch": "crouch",
    "Prone": "prone",
    "DropItem": "drop",
    "ShowMyInventory": "inventory",
    "AccessInventory": "target_inventory",
    "ToggleHUDHidden": "toggle_hud",
    "ShowExtendedInfo": "hud_info",
    "TransferItem": "transfer",
    "Use": "use",
    "ShowTribeManager": "logs",
    "UseItem1": "hotbar_1",
    "UseItem2": "hotbar_2",
    "UseItem3": "hotbar_3",
    "UseItem4": "hotbar_4",
    "UseItem5": "hotbar_5",
    "UseItem6": "hotbar_6",
    "UseItem7": "hotbar_7",
    "UseItem8": "hotbar_8",
    "UseItem9": "hotbar_9",
    "UseItem10": "hotbar_0",
    "TransferItem": "transfer",
}

_REPLACE = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]
