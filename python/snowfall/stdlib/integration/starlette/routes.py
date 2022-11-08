import os
import re
from typing import Sequence

import httpx
from starlette import endpoints, requests, responses, routing

from snowfall.stdlib.integration.starlette import models


class Proxy(object):
    def __init__(
        self,
        client: httpx.AsyncClient,
        allow: Sequence[tuple[str, re.Pattern[str]]] | None = None,
        deny: Sequence[tuple[str, re.Pattern[str]]] | None = None,
    ) -> None:
        if not str(client.base_url):
            raise RuntimeError("A base URL must be set to use the proxy route")

        if allow and deny:
            raise RuntimeError("allow and deny can't both be specified")

        self._allow = allow
        self._client = client
        self._deny = deny

    def to_route(self, prefix: str = "") -> routing.Route:
        return routing.Route(
            "/{0}".format(os.path.join(prefix, "{path:path}").lstrip("/")),
            endpoint=self._route,
            methods=["POST", "GET", "PATCH", "DELETE"],
        )

    async def _route(
        self,
        request: requests.Request,
    ) -> responses.Response:
        response = await self._client.request(
            method=request.method,
            url="{0}?{1}".format(request.url.path, request.url.query),
            content=await request.body(),
        )

        their_base_url = str(self._client.base_url).encode()
        our_base_url = str(
            self._client.base_url.copy_with(
                scheme="https" if request.url.is_secure else "http",
                host=request.url.hostname,
                port=request.url.port,
                # todo: take prefix into consideration
            ),
        ).encode()

        return responses.Response(
            content=response.content.replace(their_base_url, our_base_url),
            status_code=response.status_code,
            media_type=response.headers["Content-Type"],
        )


class Health(endpoints.HTTPEndpoint):
    async def get(self, request: requests.Request) -> responses.Response:
        return models.JsonApiResponse(
            models.Body(
                meta={"status": "pass"},
                links={"self": str(request.url_for("Health"))},
            ),
        )
