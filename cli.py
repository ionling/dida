import json

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
def to_file(file: str, url: str):
    """Download the JSON from the URL and save it to a file."""
    r = client.request("GET", url)
    with open(file, "w") as f:
        f.write(json.dumps(r.json(), indent=2))


@app.command()
def archive(months_ago: int = 1):
    now = arrow.now()
    tasks = client.list_tasks(now.shift(months=-months_ago), now)
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
                client.delete_task(t.project_id, t.id)
                typer.secho(f"Deleted {index} {t.title}", fg="red")
            else:
                dao.create_task(t)
                client.delete_task(t.project_id, t.id)
                typer.secho(f"Archived {index} {t.title}", fg="green")


if __name__ == "__main__":
    try:
        app()
    finally:
        # Fix `TypeError: 'NoneType' object is not callable`
        client.close()
