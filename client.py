import arrow
import httpx

from model import Task


class Client:
    _api_v2 = "https://api.dida365.com/api/v2"

    def __init__(self, cookie: str):
        headers = {"cookie": cookie}
        self._client = httpx.Client(headers=headers)

    def close(self):
        self._client.close()

    def list_projects(self):
        url = f"{self._api_v2}/projects"
        r = self._client.get(url)
        raise Exception("unimplemented")

    def list_tasks(self, start: arrow.Arrow, end: arrow.Arrow) -> list[Task]:
        # https://api.dida365.com/api/v2/date/2021-08-01T00:00:00.000+0800/to/2021-09-05T00:00:00.000+0800/tasks?timezone=
        url = f"{self._api_v2}/date/{start}/to/{end}/tasks"
        url = url.replace("08:00", "0800")
        r = self._client.get(url)
        r.raise_for_status()
        return [self._task_from_json(i) for i in r.json()]

    def delete_task(
        self,
        project_id: str,
        task_id: str,
    ):
        url = f"{self._api_v2}/batch/task"
        r = self._client.post(
            url,
            json={"delete": [{"taskId": task_id, "projectId": project_id}]},
        )
        r.raise_for_status()

    @staticmethod
    def _task_from_json(j: dict) -> Task:
        created_at = arrow.get(j["createdTime"]).datetime
        schedule = arrow.get(j["startDate"]).datetime
        return Task(
            id=j["id"],
            project_id=j.get("projectId", ""),
            title=j["title"],
            content=j.get("content", ""),  # content may not exit
            done=bool(j.get("completedTime", "")),
            schedule=schedule,
            created_at=created_at,
        )
