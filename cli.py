import arrow
import typer

import dao
from client import Client

COOKIE_FILE = ".cookie"


def get_cookie() -> str:
    with open(COOKIE_FILE) as f:
        return f.read().strip()


app = typer.Typer()
client = Client(get_cookie())


@app.command()
def archive():
    now = arrow.now()
    tasks = client.list_tasks(now.shift(months=-1), now)
    tasks = list(filter(lambda x: not x.done, tasks))
    batch_size = 30
    while True:
        batch, tasks = tasks[:batch_size], tasks[batch_size:]
        if len(batch) == 0:
            break

        for i, t in enumerate(batch):
            # TODO: Pretty with table
            print(
                f"Created at: {t.created_at.date()}, Index: {i:2}, "
                f"Title: {t.title}, Content: {t.content}"
            )

        while True:
            inp = input("Archive (index/c[ontinue] (default)/b[reak])? ")
            if inp == "":
                break
            if inp == "c":
                break
            if inp == "b":
                return

            index = int(inp)
            if index > len(batch) - 1:
                typer.secho(f"Index out of range", fg="red")
                continue

            t = batch[index]
            dao.create_task(t)
            client.delete_task(t.project_id, t.id)


if __name__ == "__main__":
    try:
        app()
    finally:
        # Fix `TypeError: 'NoneType' object is not callable`
        client.close()
