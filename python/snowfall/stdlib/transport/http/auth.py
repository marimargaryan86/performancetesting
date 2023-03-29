from typing import AsyncGenerator

import httpx


class TokenAuth(httpx.Auth):
    def __init__(self, token: str):
        self._token = token

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers.update(
            httpx.Headers(
                {
                    "Authorization": "Bearer {0}".format(self._token),
                },
            ),
        )
        yield request
