from datetime import datetime
import json
import sys

import arrow
import typer

import dao
from client import Client, task_from_json

COOKIE_FILE = ".cookie"


def get_cookie() -> str:
    with open(COOKIE_FILE) as f:
        return f.read().strip()


app = typer.Typer()
clt = Client(get_cookie())


@app.command()
def to_file(file: str, url: str):
    """Download the JSON from the URL and save it to a file."""
    r = clt.request("GET", url)
    with open(file, "w") as f:
        f.write(json.dumps(r.json(), indent=2))


@app.command()
def archive(months_ago: int = 1):
    now = arrow.now()
    tasks = clt.list_tasks(now.shift(months=-months_ago), now)
    tasks = list(filter(lambda x: not x.done, tasks))
    tasks.sort(key=lambda x: x.schedule)
    batch_size = 30
    while True:
        batch, tasks = tasks[:batch_size], tasks[batch_size:]
        if len(batch) == 0:
            break

        for i, t in enumerate(batch):
            # TODO: Pretty with table
            print(
                f"Created at: {t.created_at}, "
                f"Schedule: {t.schedule}, "
                f"Index: {i:2}, "
                f"Title: {t.title}",
                f"Content: {t.content}",
            )

        while True:
            inp = input("Archive (index/c[ontinue]/d(elete) (default)/b[reak])? ")
            if inp == "":
                break
            if inp == "c":
                break
            if inp == "b":
                return

            op = ""
            if inp.startswith("d"):
                inp = inp[1:]
                op = "delete"

            index = int(inp)
            if index > len(batch) - 1:
                typer.secho(f"Index out of range", fg="red")
                continue

            t = batch[index]
            if op == "delete":
                clt.delete_task(t.project_id, t.id)
                typer.secho(f"Deleted {index} {t.title}", fg="red")
            else:
                dao.create_task(t)
                clt.delete_task(t.project_id, t.id)
                typer.secho(f"Archived {index} {t.title}", fg="green")


@app.command()
def add_json():
    """Parse the task JSON from stdin and save it."""
    s = sys.stdin.read()
    j = json.loads(s)
    t = task_from_json(j)
    dao.create_task(t)


@app.command()
def random(n: int = 10):
    """Display some random tasks"""
    for t in dao.random(n):
        print(t)


if __name__ == "__main__":
    try:
        app()
    finally:
        # Fix `TypeError: 'NoneType' object is not callable`
        clt.close()
