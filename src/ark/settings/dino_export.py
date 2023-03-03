from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import dacite

from .. import config


@dataclass
class DinoExport:

    dino_name: str
    tamed_name: str
    health: float
    stamina: float
    oxygen: float
    food: float
    weight: float
    melee: float
    speed: float
    crafting: float

    @staticmethod
    def load_most_recent(path: Optional[str] = None) -> DinoExport:
        """Loads the settings from input.ini, using the `ARK_PATH` provided
        in the configs or an alternatively passed path."""
        if path is None:
            path = f"{config.ARK_PATH}\ShooterGame\Saved\DinoExports"
            
        if "common" in path:
            id_folder = max(
                [p for p in Path(path).iterdir()],
                key=lambda p: datetime.fromtimestamp(p.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
            path += f"\{id_folder.stem}"

        file = max(
            [p for p in Path(path).iterdir()],
            key=lambda p: datetime.fromtimestamp(p.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        settings: dict[str, str | float] = {}
        try:
            with open(file, encoding="utf-8") as f:
                contents = f.readlines()
        except UnicodeDecodeError:
            with open(file, encoding="utf-16") as f:
                contents = f.readlines()

        for line in contents:
            line = line.strip()
            if line.count("=") != 1:
                continue

            key, val = line.split("=")
            action = _KEY_MAP.get(key)
            if action is None:
                continue
            try:
                settings[action] = float(val)
            except ValueError:
                settings[action] = val

        return dacite.from_dict(DinoExport, settings)


_KEY_MAP = {
    "DinoNameTag": "dino_name",
    "TamedName": "tamed_name",
    "Health": "health",
    "Stamina": "stamina",
    "Oxygen": "oxygen",
    "food": "food",
    "Weight": "weight",
    "Melee Damage": "melee",
    "Movement Speed": "speed",
    "Crafting Skill": "crafting",
}
