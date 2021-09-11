from datetime import datetime

from pony.orm import *

import model

DB_FILE = "dida.db3"

db = Database()


class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    content = Optional(str, default="")
    schedule = Optional(datetime)
    created_at = Optional(datetime, default=datetime.now())

    _table_ = "taskn"


@db_session
def create_task(t: model.Task):
    Task(title=t.title, content=t.content, schedule=t.schedule, created_at=t.created_at)


db.bind(provider="sqlite", filename=DB_FILE)
db.generate_mapping()
