import arrow
import httpx
from loguru import logger

from model import Task


class Client:
    _api_v2 = "https://api.dida365.com/api/v2"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"

    def __init__(self, cookie: str):
        headers = {"cookie": cookie, "user-agent": self.user_agent}
        self._client = httpx.Client(headers=headers)

    def close(self):
        self._client.close()

    def request(self, method: str, url: str):
        return self._client.request(method, url)

    def list_projects(self):
        url = f"{self._api_v2}/projects"
        r = self._client.get(url)
        raise Exception("unimplemented")

    def list_tasks(self, start: arrow.Arrow, end: arrow.Arrow) -> list[Task]:
        # https://api.dida365.com/api/v2/date/2021-08-01T00:00:00.000+0800/to/2021-09-05T00:00:00.000+0800/tasks?timezone=
        url = f"{self._api_v2}/date/{start}/to/{end}/tasks"
        url = url.replace("08:00", "0800")
        ctxl = logger.bind(url=url)
        ctxl.debug("http get")
        try:
            r = self._client.get(url)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            ctxl.bind(
                status=e.response.status_code, content=e.response.content
            ).warning("bad status")
            raise e
        return [task_from_json(i) for i in r.json()]

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


def task_from_json(j: dict) -> Task:
    created_at = arrow.get(j["createdTime"]).to("local").datetime
    schedule = arrow.get(j["startDate"]).to("local").datetime
    return Task(
        id=j["id"],
        project_id=j.get("projectId", ""),
        title=j["title"],
        content=j.get("content", ""),  # content may not exit
        done=bool(j.get("completedTime", "")),
        schedule=schedule,
        created_at=created_at,
    )
