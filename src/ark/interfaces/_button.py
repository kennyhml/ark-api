from dataclasses import dataclass
from typing import Optional
from .._ark import Ark
from .._tools import get_filepath

@dataclass
class Button:

    location: tuple[int, int]
    region: Optional[tuple[int, int, int, int]] = None
    template: Optional[str] = None

    def __post_init__(self) -> None:
        if self.template is None:
            return
        template = f"{Ark.PKG_DIR}/assets/interfaces/{self.template}"
        self.template = get_filepath(template)