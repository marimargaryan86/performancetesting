from collections.abc import Mapping, Sequence
from typing import Any

import httpx


class BaseClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self._client = create_httpx_client(
            base_url=base_url,
            auth=auth,
            client=client,
        )

    async def _make_request(  # noqa: WPS211
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        headers: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.request(
            method=method,
            url=url,
            params=query_parameters,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        return response.json()


def create_httpx_client(
    base_url: str,
    auth: httpx.Auth | None = None,
    client: httpx.AsyncClient | None = None,
) -> httpx.AsyncClient:
    client = client or httpx.AsyncClient()
    client.base_url = httpx.URL(base_url)
    client.headers.update(
        httpx.Headers(
            {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            },
        ),
    )

    if auth:
        client.auth = auth

    return client


def make_pagination_params(
    limit: int | None,
    cursor: str | None,
    sort: str | None = None,
    include: Sequence[str] | None = None,
) -> dict[str, int | str]:
    pagination_params: dict[str, int | str] = {}
    if limit:
        pagination_params["page[limit]"] = limit
    if cursor:
        pagination_params["page[cursor]"] = cursor
    if sort:
        pagination_params["sort"] = sort
    if include:
        pagination_params["include"] = ",".join(include)
    return pagination_params
