from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class TaskStatus(Enum):
    ABANDONED = auto()


@dataclass
class Task:
    id: str
    title: str
    schedule: datetime
    created_at: datetime
    project_id: str = ""
    content: str = ""
    done: bool = False
