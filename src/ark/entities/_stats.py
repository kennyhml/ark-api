
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Stats:
    health: int
    food: int
    water: int
    weight: int
    stamina: Optional[int] = None
    oxygen: Optional[int] = None
    melee: Optional[int] = None
    speed: Optional[int] = None
    crafting: Optional[int] = None
    fortitude: Optional[int] = None