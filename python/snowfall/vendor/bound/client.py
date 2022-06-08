from __future__ import annotations

import time
from typing import Any

import httpx
import jwt

from snowfall.vendor.bound.models import exchange


def _is_valid_token(token: str) -> bool:
    decoded = jwt.decode(token, options={"verify_signature": False})

    return decoded["exp"] < int(time.time())


def _auth_required(func: Any) -> Any:
    async def wrapper(self: Bound, *args: Any, **kwargs: Any) -> None:

        if not self._auth_cookies or _is_valid_token(self._auth_cookies["jwt"]):
            await self._authenticate()

        return await func(self, *args, **kwargs)

    return wrapper


class Bound(object):
    def __init__(self, base_url: str, email: str, password: str):
        self._base_url = base_url
        self._email = email
        self._password = password
        self._http_client = httpx.AsyncClient(verify=False)
        self._auth_cookies: dict[str, Any] = {}

    @_auth_required
    async def quote(
        self,
        buy_currency: str,
        sell_currency: str,
        amount: float,
    ) -> exchange.Quote:
        quote_data = {
            "knownQuantity": {
                "amount": amount,
                "currency": sell_currency,
            },
            "otherCurrency": buy_currency,
            "sendKnown": True,
        }

        response = await self._http_client.post(
            "{0}/v1/spots/quotes".format(self._base_url),
            cookies=self._auth_cookies,
            json=quote_data,
        )

        response.raise_for_status()
        response_data = response.json()

        return exchange.Quote(
            amount=response_data["sell"]["amount"],
            buy_currency=response_data["buy"]["currency"],
            sell_currency=response_data["sell"]["currency"],
        )

    @_auth_required
    async def create_spot(self, quote_id: str) -> dict[str, Any]:
        quote_data = {"quoteId": quote_id}

        response = await self._http_client.post(
            "{0}/v1/spots/".format(self._base_url),
            cookies=self._auth_cookies,
            json=quote_data,
        )

        response.raise_for_status()

        return response.json()

    @_auth_required
    async def get_spot(self, spot_id: str) -> dict[str, Any]:
        spot_url = "{0}/v1/spots/{1}".format(self._base_url, spot_id)
        response = await self._http_client.get(
            spot_url,
            cookies=self._auth_cookies,
        )

        response.raise_for_status()

        return response.json()

    async def _authenticate(self) -> None:
        credentials = {
            "email": self._email,
            "password": self._password,
        }
        response = await self._http_client.post(
            "{0}/v1/login".format(self._base_url),
            json=credentials,
        )

        response.raise_for_status()

        self._auth_cookies = self._get_jwt_from_cookie(response.headers["Set-Cookie"])

    def _get_jwt_from_cookie(self, cookie: str) -> dict[str, Any]:
        jwt_part = cookie.split(";")[0]

        token = jwt_part.split("=")

        return {token[0]: token[1]}
