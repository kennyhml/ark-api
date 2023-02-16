from dataclasses import dataclass


@dataclass
class TribeLogMessage:
    """Represents a single message in the tribe log"""

    day: str
    action: str
    content: str

    def __repr__(self):
        return f"{self.day} {self.action} {self.content}"