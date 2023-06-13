from __future__ import annotations

import dataclasses
from collections.abc import AsyncIterable, Iterable
from typing import Any, Literal

import httpx

from snowfall.stdlib.transport.http import errors


@dataclasses.dataclass(frozen=True)
class RequestOptions(object):
    method: Literal[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "OPTIONS",
        "DELETE",
        "HEAD",
    ]
    path: str
    query: dict[str, str] | None = None
    payload: Any | None = None
    raw_content: str | bytes | Iterable[bytes] | AsyncIterable[bytes] | None = None
    headers: dict[str, str] | None = None


class HttpClient(object):
    def __init__(self, base_url: str, http_client: httpx.AsyncClient):
        self._base_url = httpx.URL(base_url)
        self._http_client = http_client

    async def _make_request(self, options: RequestOptions) -> httpx.Response:
        try:
            response = await self._http_client.request(
                method=options.method,
                url=self._base_url.copy_with(path=options.path, params=options.query),
                headers=options.headers,
                json=options.payload,
                content=options.raw_content,
            )
        except httpx.TimeoutException as timeout_exc:
            raise errors.TimeOutError.from_error(timeout_exc) from timeout_exc
        except httpx.RequestError as request_exc:
            raise errors.RequestError.from_error(request_exc) from request_exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise errors.HttpStatusError.from_error(exc) from exc

        return response
