import dataclasses

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
