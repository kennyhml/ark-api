from dataclasses import dataclass
from typing import Optional


@dataclass
class Server:
    name: str
    status: Optional[str] = None
    day: Optional[str] = None
    ip: Optional[str] = None
    game_port: Optional[str] = None
    query_port: Optional[str] = None
