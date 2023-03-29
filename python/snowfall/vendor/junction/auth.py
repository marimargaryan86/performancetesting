import time
from typing import AsyncGenerator

import httpx
import jwt


class UserAuth(httpx.Auth):
    def __init__(
        self,
        base_url: str,
        email: str,
        password: str,
    ):
        self._base_url = base_url
        self._email = email
        self._password = password
        self._token = ""  # nosec
        self._http_client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
            },
            base_url=base_url,
            http2=True,
        )

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

        response = await self._http_client.post(
            url="/users/tokens",
            json=payload,
        )

        response.raise_for_status()

        response_data = response.json()
        return response_data["data"]["attributes"]["token"]
