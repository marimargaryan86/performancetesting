import asyncio
from collections.abc import AsyncGenerator, Mapping
from typing import Any

import httpx

from snowfall.stdlib.logging import stdout
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.rate import (
    BasicRateResponse,
    DetailedRateRequest,
    DetailedRateResponse,
)

_METHOD_GET = "GET"
_METHOD_POST = "POST"


class CurrencyCloudAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self,
        base_url: str,
        login_id: str,
        api_key: str,
        client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url
        self._login_id = login_id
        self._api_key = api_key
        self._token = self._initiate_token()
        self._async_lock = asyncio.Lock()
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(base_url)
        self._logger = stdout.get_logger()

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers["X-Auth-Token"] = self._token
        response = yield request

        if response.status_code == httpx.codes.UNAUTHORIZED:
            async with self._async_lock:
                if self._token == request.headers["X-Auth-Token"]:
                    self._logger.info("Getting token")
                    await self._authenticate()

            request.headers["X-Auth-Token"] = self._token
            yield request

    async def _authenticate(self) -> None:
        response = (
            await self._client.post(
                url="/authenticate/api",
                data={
                    "login_id": self._login_id,
                    "api_key": self._api_key,
                },
            )
        ).json()

        if response.get("error_code") == "auth_failed":
            raise CurrencyCloudError(
                [response["error_messages"]["username"][0]["message"]],
            )

        self._token = response["auth_token"]

    def _initiate_token(self) -> str:
        response = (
            httpx.post(
                url="{0}/authenticate/api".format(self._base_url),
                data={
                    "login_id": self._login_id,
                    "api_key": self._api_key,
                },
            )
        ).json()

        if response.get("error_code") == "auth_failed":
            raise CurrencyCloudError(
                [response["error_messages"]["username"][0]["message"]],
            )

        return response["auth_token"]


def encode_arrays(
    payload: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    encoded_payload: dict[str, Any] = {}
    if payload is None:
        return encoded_payload

    for payload_key, payload_value in payload.items():
        if isinstance(payload_value, list):
            encoded_payload["{0}[]".format(payload_key)] = payload_value
        else:
            encoded_payload[payload_key] = payload_value

    return encoded_payload


def remove_blank_string(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    return {
        key: payload_val for key, payload_val in payload.items() if payload_val != ""
    }


class PaymentClient:
    def __init__(
        self,
        base_url: str,
        auth: CurrencyCloudAuth,
        client: httpx.AsyncClient | None = None,
    ):
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(base_url)
        self._client.auth = auth
        self._logger = stdout.get_logger()

    async def get_detailed_rates(
        self,
        detailed_rates_request: DetailedRateRequest,
    ) -> DetailedRateResponse:
        if detailed_rates_request.sell_currency == detailed_rates_request.buy_currency:
            return DetailedRateResponse(
                client_buy_currency=detailed_rates_request.buy_currency,
                client_sell_currency=detailed_rates_request.sell_currency,
                client_buy_amount=detailed_rates_request.amount,
            )
        return DetailedRateResponse(
            **await self._make_request(
                method=_METHOD_GET,
                url="rates/detailed",
                query_parameters=detailed_rates_request.dict(exclude_none=True),
            ),
        )

    async def get_basic_rates(self, currency_pairs: str) -> list[BasicRateResponse]:
        response = await self._client.get(
            "/rates/find",
            params={
                "currency_pair": currency_pairs,
            },
        )
        response.raise_for_status()
        response_data = response.json()

        if response_data["unavailable"]:
            self._logger.error(
                "Unavailable currency pairs",
                pairs=",".join(response_data["unavailable"]),
            )

        return [
            BasicRateResponse(
                sell_currency=pair[:3],
                buy_currency=pair[3:],
                rate=rates[1],
            )
            for pair, rates in response_data["rates"].items()
        ]

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any] | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=query_parameters,
                data=encode_arrays(payload),
            )
        except httpx.ReadTimeout as exc:
            raise CurrencyCloudError(messages=["{0}".format(exc)]) from exc

        if response.is_client_error:
            error_messages = response.json()["error_messages"]
            raise CurrencyCloudError(
                [
                    error_message["message"]
                    for error_type, errors in error_messages.items()
                    for error_message in errors
                ],
            )

        response.raise_for_status()

        return response.json()
