from typing import Any, AsyncGenerator, Mapping

import httpx


class TokenAuth(httpx.Auth):
    def __init__(
        self,
        token: str,
        headers: Mapping[str, Any],
    ):
        self._token = token
        self._headers = headers

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
