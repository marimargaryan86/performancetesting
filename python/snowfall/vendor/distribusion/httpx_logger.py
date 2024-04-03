import datetime
import json
from pathlib import Path

import aiofiles
import httpx

from snowfall.stdlib.logging import stdout


class LogHandler:
    def __init__(
        self,
        base_url: str | None = None,
        log_path: Path | None = None,
    ) -> None:
        self.base_url = base_url
        self.log_path = log_path if log_path else Path("logs")

    def get_file_path(self) -> Path:
        date = datetime.datetime.now(tz=datetime.UTC).date()
        return self.log_path / date.isoformat()

    def get_file_name(self, url: str, suffix: str) -> str:
        if self.base_url and url.startswith(self.base_url):
            op_name = url[len(self.base_url) :]
            name = op_name.replace("/", "-").replace("_", "-")
        else:
            name = url.split("/")[-1]

        rq_time = datetime.datetime.now(tz=datetime.UTC).time()
        stamp = rq_time.isoformat(timespec="seconds").replace(":", "-")

        return "{stamp}-{name}{suffix}.json".format(
            name=name.lower(),
            stamp=stamp,
            suffix=suffix,
        )


class RequestLogHandler(LogHandler):
    def __init__(
        self,
        base_url: str | None = None,
        log_path: Path | None = None,
    ) -> None:
        super().__init__(base_url=base_url, log_path=log_path)
        self._logger = stdout.get_logger()

    async def __call__(self, request: httpx.Request) -> None:
        self._logger.info("Request", url=request.url, headers=request.headers)

        if request.content and request.headers.get("content-type"):
            rq_content = request.content.decode("utf-8")
            self._logger.info("Request", content=rq_content)

            if rq_content:
                file_path = self.get_file_path()
                file_name = self.get_file_name(request.url.path, "-rq")
                file_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(
                    file_path / file_name,
                    "w",
                    encoding="utf-8",
                ) as log_file:
                    await log_file.write(rq_content)


class ResponseLogHandler(LogHandler):
    def __init__(
        self,
        base_url: str | None = None,
        log_path: Path | None = None,
    ) -> None:
        super().__init__(base_url=base_url, log_path=log_path)
        self._logger = stdout.get_logger()

    async def __call__(self, response: httpx.Response) -> None:
        await response.aread()

        if self._has_json_content(response):
            json_data = json.loads(response.content)
            file_path = self.get_file_path()
            file_name = self.get_file_name(response.url.path, "-rs")
            file_path.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(
                file_path / file_name,
                "w",
                encoding="utf-8",
            ) as log_file:
                await log_file.write(json.dumps(json_data, ensure_ascii=False))

            self._logger.info(
                "Response",
                header=response.headers,
                status_code=response.status_code,
            )

    def _has_json_content(self, response: httpx.Response) -> bool:
        if response.headers:
            content_type = response.headers.get("content-type")
            return (
                content_type
                and content_type.startswith("application/")
                and "json" in content_type
            )

        return False


def with_logging(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    registered_hooks = http_client.event_hooks
    registered_hooks["request"].append(
        RequestLogHandler(http_client.base_url.path, None),
    )
    registered_hooks["response"].append(
        ResponseLogHandler(http_client.base_url.path, None),
    )
    http_client.event_hooks = registered_hooks
    return http_client
