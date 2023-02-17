from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import dacite

from ..config import ARK_PATH


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
            path = f"{ARK_PATH}\Saved\Config\WindowsNoEditor\Input.ini"

        with open(path) as f:
            contents = f.readlines()

        settings: dict[str, float | bool | str | Path] = {}
        settings["path"] = Path(path)

        for line in contents:
            if line.startswith("[/Script/Engine.Console]"):
                break

            if not "=" in line:
                continue

            if "ConsoleKeys" in line:
                action_name = "ConsoleKeys"
                key = line.split("=")[1].strip()
            else:
                pattern = r'ActionName="([^"]+)",Key=([^,]+)'
                matches = re.search(pattern, line)
                if not matches:
                    continue

                action_name = matches.group(1)
                key = matches.group(2)

            action = _KEY_MAP.get(action_name)
            if action is not None:
                settings[action] = key

        return dacite.from_dict(InputSettings, settings)


_KEY_MAP = {
    "ConsoleKeys": "console",
    "CrouchProneToggle": "crouch",
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
}
