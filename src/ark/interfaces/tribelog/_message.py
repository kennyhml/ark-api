from dataclasses import dataclass


@dataclass
class TribeLogMessage:
    """Represents a single message in the tribe log"""

    day: str
    action: str
    content: str

    def __repr__(self):
        return f"{self.day} {self.action} {self.content}"
    

    def __post_init__(self) -> None:
        self.day = f"Day {self.day[4:]}" 
