import time
from collections.abc import AsyncGenerator

import httpx
import jwt

from snowfall.stdlib.format import jsonapi
from snowfall.vendor.junction import client as base_client


class UserAuth(base_client.BaseClient, httpx.Auth):
    def __init__(
        self,
        base_url: str,
        email: str,
        password: str,
        client: httpx.AsyncClient | None = None,
    ):
        self._email = email
        self._password = password
        self._token = ""  # nosec
        super().__init__(base_url=base_url, client=client)

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        if not self._is_token_valid():
            self._token = await self._create_authentication_token()

        request.headers.update({"Authorization": "Bearer {0}".format(self._token)})
        yield request

    def _is_token_valid(self) -> bool:
        if self._token:
            decoded = jwt.decode(self._token, options={"verify_signature": False})

            return int(time.time()) < decoded["exp"]
        return False

    async def _create_authentication_token(
        self,
    ) -> str:
        payload = {
            "data": {
                "type": "user-tokens",
                "attributes": {
                    "email": self._email,
                    "password": self._password,
                },
            },
        }

        response = await self.client.post(
            url="/users/tokens",
            json=payload,
        )

        response.raise_for_status()

        response_data = jsonapi.flatten_resource(response.json()["data"])
        return response_data["token"]
