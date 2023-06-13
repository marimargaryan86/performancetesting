from collections.abc import Generator

import httpx


class TokenAuth(httpx.Auth):
    def __init__(self, token: str):
        self._token = token

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers.update(
            httpx.Headers(
                {
                    "Authorization": "Bearer {0}".format(self._token),
                },
            ),
        )
        yield request
