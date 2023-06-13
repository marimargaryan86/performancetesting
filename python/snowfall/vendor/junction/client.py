from collections.abc import Sequence

import httpx


class BaseClient(object):
    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = httpx.URL(base_url)
        self.client = client or httpx.AsyncClient()
        self.client.base_url = self._base_url
        self.client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

        if auth:
            self.client.auth = auth


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
