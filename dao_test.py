from datetime import datetime

import dao
import model


def test_task():
    now = datetime.now().astimezone()
    t1 = model.Task(
        id="unit-test",
        title="test",
        schedule=now,
        created_at=now,
    )
    dao.create_task(t1)


def test_random():
    tasks = dao.random()
    assert len(tasks) == 10
