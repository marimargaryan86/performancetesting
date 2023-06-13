import asyncio
import inspect
from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import ValidationError

from snowfall.vendor.duffel import errors
from snowfall.vendor.duffel.builders.offer_request import OfferRequestData
from snowfall.vendor.duffel.builders.order_cancel import OrderCancelRequest
from snowfall.vendor.duffel.builders.order_request import OrderData
from snowfall.vendor.duffel.models.cancel_pending import CancelData, CancelResponse
from snowfall.vendor.duffel.models.errors import ErrorResponse
from snowfall.vendor.duffel.models.offer import Offer
from snowfall.vendor.duffel.models.offer_request import (
    OfferRequest,
    OfferRequestResponse,
)
from snowfall.vendor.duffel.models.order import Order, OrderResponse
from snowfall.vendor.duffel.models.seat_map import SeatResponse, Seats
from snowfall.vendor.duffel.models.single_offer import SingleOfferResponse
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


def _get_response_error_message(response: httpx.Response) -> str:
    try:
        errors_response = ErrorResponse.parse_raw(response.content)
    except ValidationError:
        return "can't parse error"

    error_status = str(errors_response.meta.status if errors_response.meta else "")
    error_title = errors_response.errors[0].title if errors_response.errors else ""
    error_message = errors_response.errors[0].message if errors_response.errors else ""
    return "{0}: {1}, {2}".format(error_status, error_title, error_message)


class DuffelClient(object):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        api_base_url: str,
        api_key: str,
        version: str,
        http_client: httpx.AsyncClient,
        rate_limit_client: RateLimitClient,
    ) -> None:
        self._token = api_key
        self._version = version
        self._http_client = http_client
        self._http_client.base_url = httpx.URL(api_base_url)
        self._rate_limit_client = rate_limit_client

    async def create_offer_request(
        self,
        offer_request_data: OfferRequestData,
        rate_limit_timeout: float = 60,
    ) -> OfferRequest:
        response = await self._make_request(
            "POST",
            "/air/offer_requests",
            payload=offer_request_data.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return OfferRequestResponse.parse_raw(response.content).response_data

    async def get_single_offer(
        self,
        offer_id: str,
        rate_limit_timeout: float = 60,
    ) -> Offer:
        response = await self._make_request(
            "GET",
            "air/offers/{id}".format(id=offer_id),
            rate_limit_timeout=rate_limit_timeout,
        )

        return SingleOfferResponse.parse_raw(response.content).response_data

    async def get_seat_map(
        self,
        offer_id: str,
        rate_limit_timeout: float = 60,
    ) -> list[Seats]:
        response = await self._make_request(
            "GET",
            "air/seat_maps",
            query_params={"offer_id": offer_id},
            rate_limit_timeout=rate_limit_timeout,
        )

        return SeatResponse.parse_raw(response.content).response_data

    async def order_request(
        self,
        order_data: OrderData,
        rate_limit_timeout: float = 60,
    ) -> Order:
        response = await self._make_request(
            "POST",
            "/air/orders",
            payload=order_data.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return OrderResponse.parse_raw(response.content).response_data

    async def get_order(
        self,
        order_id: str,
        rate_limit_timeout: float = 60,
    ) -> Order:
        response = await self._make_request(
            "GET",
            "air/orders/{id}".format(id=order_id),
            rate_limit_timeout=rate_limit_timeout,
        )

        return OrderResponse.parse_raw(response.content).response_data

    async def cancel_order_request(
        self,
        cancel_data: OrderCancelRequest,
        rate_limit_timeout: float = 60,
    ) -> CancelData:
        response = await self._make_request(
            "POST",
            "/air/order_cancellations",
            payload=cancel_data.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return CancelResponse.parse_raw(response.content).response_data

    async def cancel_order_confirm(
        self,
        cancel_id: str,
        rate_limit_timeout: float = 60,
    ) -> CancelData:
        response = await self._make_request(
            "POST",
            "/air/order_cancellations/{id}/actions/confirm".format(id=cancel_id),
            rate_limit_timeout=rate_limit_timeout,
        )

        return CancelResponse.parse_raw(response.content).response_data

    async def _make_request(  # noqa: WPS211
        self,
        method: str,
        path: str,
        query_params: Mapping[str, Any] | None = None,
        payload: Any | None = None,
        rate_limit_timeout: float = 60,
    ) -> httpx.Response:
        try:  # noqa: WPS229
            await self._rate_limit_client.rate_limit(timeout=rate_limit_timeout)
            response = await self._http_client.request(
                method=method,
                url=path,
                params=query_params,
                content=payload,
                headers={
                    "Authorization": "Bearer {token}".format(token=self._token),
                    "Accept-Encoding": "gzip",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Duffel-Version": self._version,
                },
            )
        except (httpx.HTTPError, asyncio.TimeoutError) as raw_exc:
            raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError(_get_response_error_message(response)) from exc

        return response
