from dataclasses import dataclass
from typing import Optional


@dataclass
class Server:
    name: str
    ip: Optional[str] = None
    
