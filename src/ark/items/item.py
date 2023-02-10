import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    """Represents an ark item"""

    name: str
    search_name: str
    stack_size: int
    inventory_icon: str
    added_icon: Optional[str] = None
    added_text: Optional[str] = None
    min_len_deposits: Optional[int] = None

    def __hash__(self) -> int:
        return hash(self.name)

    def __post_init__(self) -> None:
        for path in (self.inventory_icon, self.added_icon, self.added_text):
            if path is None:
                continue
            assert os.path.exists(path), f"Path not found: {path}"