from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Channel:
    id: str
    name: str
    aliases: List[str] = field(default_factory=list)


@dataclass
class Programme:
    channel_id: str
    title: str
    start: datetime
    stop: datetime

    description: Optional[str] = None
    category: Optional[str] = None

    source: Optional[str] = None

    def key(self):
        return (
            self.channel_id,
            self.title.strip().lower(),
            self.start.replace(second=0, microsecond=0)
        )