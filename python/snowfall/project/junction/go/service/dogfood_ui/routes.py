import lagom
from starlette import endpoints, requests, responses, templating

from snowfall.stdlib import string

_SESSION_TOKEN_LENGTH = 32


class UI(endpoints.HTTPEndpoint):
    async def get(
        self,
        request: requests.Request,
        template: templating.Jinja2Templates = lagom.injectable,
    ) -> responses.Response:
        return template.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "session_token": string.random(_SESSION_TOKEN_LENGTH),
            },
        )
