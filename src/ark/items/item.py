from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .._helpers import get_filepath


@dataclass
class Item:
    """Represents an ark item"""

    name: str
    search_name: str
    stack_size: int
    inventory_icon: str
    recipe: Optional[dict[Item, int]] = None
    added_icon: Optional[str] = None
    added_text: Optional[str] = None
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def __post_init__(self) -> None:

        self.inventory_icon = get_filepath(self.inventory_icon)
        if self.added_icon is not None:
            self.added_icon = get_filepath(self.added_icon)

        if self.added_text is not None:
            self.added_text = get_filepath(self.added_text)

        for path in (self.inventory_icon, self.added_icon, self.added_text):
            if path is None:
                continue
            assert os.path.exists(path), f"Path not found: {path}"