import httpx

from snowfall.stdlib.instrumentation.httpx import _discovery  # noqa: PLC2701
from snowfall.stdlib.logging import stdout


class _ResponseHandler:
    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def __call__(self, response: httpx.Response) -> None:
        await response.aread()

        self._logger.info(
            "Response received",
            client=_discovery.get_parent_class(),
            client_method=_discovery.get_calling_method(),
            method=response.request.method,
            status_code=response.status_code,
            request_url=str(response.request.url),
            request_headers=dict(response.request.headers),
            request=response.request.content,
            response=response.content,
            response_headers=dict(response.headers),
            source="transport",
        )


def register(client: httpx.AsyncClient) -> httpx.AsyncClient:
    registered_hooks = client.event_hooks
    registered_hooks["response"].append(_ResponseHandler())
    client.event_hooks = registered_hooks

    return client
