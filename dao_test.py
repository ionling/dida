import dao
import model


def test_task():
    t1 = model.Task(title="test")
    dao.create_task(t1)
