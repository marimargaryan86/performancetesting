import json

import httpx

from snowfall.stdlib.logging import stdout


class RequestLogHandler(object):
    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def __call__(self, request: httpx.Request) -> None:
        self._logger.info("Request", url=request.url)

        if request.content and request.headers.get("content-type"):
            self._logger.info("Request", content=request.content.decode("utf-8"))


class ResponseLogHandler(object):
    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def __call__(self, response: httpx.Response) -> None:
        await response.aread()

        if has_json_content(response):
            json_data = json.loads(response.content)
            self._logger.info(
                "Response",
                status_code=response.status_code,
                content=json.dumps(json_data),
            )


def has_json_content(response: httpx.Response) -> bool:
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
    registered_hooks["request"].append(RequestLogHandler())
    registered_hooks["response"].append(ResponseLogHandler())
    http_client.event_hooks = registered_hooks
    return http_client
