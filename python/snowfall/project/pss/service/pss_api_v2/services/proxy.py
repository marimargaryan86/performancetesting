import httpx
from fastapi import Depends
from fastapi.requests import Request
from fastapi.responses import Response

from snowfall.project.pss.service.pss_api_v2.clients.httpx import (
    get_proxy_async_httpx_client,
)


class ProxyService(object):
    def __init__(
        self,
        client: httpx.AsyncClient = Depends(get_proxy_async_httpx_client),
    ) -> None:
        self._client = client

    async def proxy_request(self, request: Request) -> Response:
        resp = await self._client.request(
            method=request.method,
            url="{0}?{1}".format(request.url.path, request.url.query),
            content=await request.body(),
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers["Content-Type"],
        )
