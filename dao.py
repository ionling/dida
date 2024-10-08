from datetime import datetime

from pony.orm import (
    Database,
    Optional,
    PrimaryKey,
    Required,
    db_session,
)

import model

DB_FILE = "dida.db3"

db = Database()


class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    content = Optional(str, default="")
    schedule = Optional(datetime)
    created_at = Optional(datetime, default=datetime.now())
    col_created_at = Optional(datetime, default=datetime.now().astimezone())

    _table_ = "taskn"


@db_session
def create_task(t: model.Task):
    Task(title=t.title, content=t.content, schedule=t.schedule, created_at=t.created_at)


@db_session
def random(limit=10) -> list[model.Task]:
    q = Task.select_random(limit)
    return [
        model.Task(
            id=t.id,
            title=t.title,
            content=t.content,
            schedule=t.schedule,
            created_at=t.created_at,
        )
        for t in q
    ]


db.bind(provider="sqlite", filename=DB_FILE)
db.generate_mapping()
