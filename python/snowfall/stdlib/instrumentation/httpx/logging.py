import httpx
import structlog

from snowfall.stdlib.instrumentation.httpx import _discovery  # noqa: WPS450


class _ResponseHandler(object):
    def __init__(self) -> None:
        self._logger = structlog.get_logger(__name__)

    async def __call__(self, response: httpx.Response) -> None:
        await response.aread()

        self._logger.info(
            "Response received",
            client=_discovery.get_parent_class(),
            client_method=_discovery.get_calling_method(),
            method=response.request.method,
            status_code=response.status_code,
            request=response.request.content,
            response=response.content,
            source="transport",
        )


def register(client: httpx.AsyncClient) -> httpx.AsyncClient:
    registered_hooks = client.event_hooks
    registered_hooks["response"].append(_ResponseHandler())
    client.event_hooks = registered_hooks

    return client
