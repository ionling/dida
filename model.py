from datetime import datetime
from typing import Optional


class Task:
    def __init__(
        self,
        id="",
        project_id="",
        title="",
        content="",
        done=False,
        schedule: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.project_id = project_id
        self.title = title
        self.content = content
        self.done = done
        self.schedule = schedule
        self.created_at = created_at
