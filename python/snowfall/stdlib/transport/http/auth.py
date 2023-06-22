import asyncio
import datetime
from collections.abc import AsyncGenerator

import httpx
from authlib.integrations import httpx_client


class ClientCredentialsAuth(httpx.Auth):
    _token_refresh_threshold = datetime.timedelta(minutes=15)  # noqa: WPS432

    def __init__(self, client: httpx_client.AsyncOAuth2Client, token_endpoint: str):
        self._client = client
        self._lock = asyncio.Lock()
        self._token_endpoint = token_endpoint
        self._token: str | None = None
        self._token_expiry: datetime.datetime | None = None

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        if self._token_expiry_below_threshold():
            await self._refresh_token()

        request.headers.update(
            httpx.Headers(
                {
                    "Authorization": "Bearer {0}".format(self._token),
                },
            ),
        )

        yield request

    async def _refresh_token(self) -> None:
        async with self._lock:
            if not self._token_expiry_below_threshold():
                return

            token = await self._client.fetch_token(
                self._token_endpoint,
                grant_type="client_credentials",
            )

            self._token = token["access_token"]
            self._token_expiry = datetime.datetime.fromtimestamp(
                token["expires_at"],
                tz=datetime.UTC,
            )

    def _token_expiry_below_threshold(self) -> bool:
        if not self._token or not self._token_expiry:
            return True

        diff = self._token_expiry - datetime.datetime.now(tz=datetime.UTC)

        return diff < self._token_refresh_threshold


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
