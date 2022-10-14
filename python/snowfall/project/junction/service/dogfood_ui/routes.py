import dataclasses

import httpx
import lagom
from starlette import endpoints, requests, responses


@dataclasses.dataclass(frozen=True)
class Template(object):
    html: str


class UI(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        template: Template = lagom.injectable,
    ) -> responses.Response:
        return responses.Response(template.html)


async def proxy(
    request: requests.Request,
    client: httpx.AsyncClient = lagom.injectable,
) -> responses.Response:
    response = await client.request(
        method=request.method,
        url="{0}?{1}".format(request.url.path, request.url.query),
        content=await request.body(),
    )

    their_base_url = str(client.base_url).encode()
    our_base_url = str(
        client.base_url.copy_with(
            scheme="https" if request.url.is_secure else "http",
            host=request.url.hostname,
            port=request.url.port,
        ),
    ).encode()

    return responses.Response(
        content=response.content.replace(their_base_url, our_base_url),
        status_code=response.status_code,
        media_type=response.headers["Content-Type"],
    )
