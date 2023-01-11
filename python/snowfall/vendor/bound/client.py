from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Concatenate, ParamSpec, Sequence, TypeVar

import httpx
import jwt

from snowfall.vendor.bound.models import exchange


def _is_valid_token(token: str) -> bool:
    decoded = jwt.decode(token, options={"verify_signature": False})

    return decoded["exp"] < int(time.time())


_In = ParamSpec("_In")
_Out = TypeVar("_Out")


def _auth_required(
    func: Callable[Concatenate[Bound, _In], Awaitable[_Out]],
) -> Callable[Concatenate[Bound, _In], Awaitable[_Out]]:
    async def wrapper(self: Bound, *args: _In.args, **kwargs: _In.kwargs) -> _Out:
        if not self._auth_cookies or _is_valid_token(self._auth_cookies["jwt"]):
            await self._authenticate()

        return await func(self, *args, **kwargs)

    return wrapper


class Bound(object):
    def __init__(self, base_url: str, email: str, password: str, timeout: float = 5.0):
        self._base_url = base_url
        self._email = email
        self._password = password
        self._http_client = httpx.AsyncClient(verify=False, timeout=timeout)
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
            "sellKnown": True,
        }

        response = await self._http_client.post(
            "{0}/v1/trades/quotes".format(self._base_url),
            cookies=self._auth_cookies,
            json=quote_data,
        )

        response.raise_for_status()
        response_data = response.json()

        return exchange.Quote(
            amount=response_data["sell"]["amount"],
            buy_currency=response_data["buy"]["currency"],
            sell_currency=response_data["sell"]["currency"],
            rate=response_data["rawRate"]["conversionRate"],
        )

    @_auth_required
    async def create_spot(self, quote_id: str) -> dict[str, Any]:
        quote_data = {"quoteId": quote_id}

        response = await self._http_client.post(
            "{0}/v1/trades/".format(self._base_url),
            cookies=self._auth_cookies,
            json=quote_data,
        )

        response.raise_for_status()

        return response.json()

    @_auth_required
    async def get_spot(self, spot_id: str) -> dict[str, Any]:
        spot_url = "{0}/v1/trades/{1}".format(self._base_url, spot_id)
        response = await self._http_client.get(
            spot_url,
            cookies=self._auth_cookies,
        )

        response.raise_for_status()

        return response.json()

    @_auth_required
    async def get_rates(self, currency_pairs: str) -> Sequence[exchange.Rate]:
        rates_url = "{0}/v1/indicative-rates?currencyPairs={1}".format(
            self._base_url,
            currency_pairs,
        )

        response = await self._http_client.get(rates_url, cookies=self._auth_cookies)

        response.raise_for_status()
        rates = response.json()["indicativeRates"]

        return [
            exchange.Rate(
                buy_currency=rate["currencyPair"][:3],
                sell_currency=rate["currencyPair"][3:],
                rate=rate["midPrice"],
            )
            for rate in rates
        ]

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
