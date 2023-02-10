from __future__ import annotations

import json

from dataclasses import dataclass
import dacite

@dataclass
class Keybinds:
    console: str
    crouch: str
    drop: str
    inventory: str
    prone: str
    target_inventory: str
    toggle_hud: str
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
    def load() -> Keybinds:
        """Returns a keybinds object created from the configs."""
        with open("settings/keybinds.json") as f:
            data = json.load(f)

        return dacite.from_dict(Keybinds, data)