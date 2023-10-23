import asyncio
import inspect
from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

import httpx

from snowfall.vendor.ba_ndc import errors
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.models import (
    request_add_seat_schemas,
    request_name_correction_schemas,
    request_offer_search_schemas,
    request_order_change_schemas,
    request_order_schemas,
    response_offer_search_schemas,
    response_order_change_schemas,
    response_order_schemas,
    response_priced_offer_schemas,
    response_seat_schemas,
    response_service_schemas,
)
from snowfall.vendor.rate_limiter.client import Client as RateLimitClient


def _request_query_params(offer_id: UUID | None, order_id: UUID | None) -> Any:
    if offer_id:
        return {"offerId": offer_id}

    return {"orderId": order_id}


class BaNdcClient(object):
    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient,
        rate_limit_clients: Sequence[RateLimitClient],
    ) -> None:
        self._api_base_url = httpx.URL(api_base_url)
        self._api_key = api_key
        self._http_client = http_client
        self._http_client.base_url = self._api_base_url
        self._rate_limit_clients = rate_limit_clients

    async def get_offers(
        self,
        request: request_offer_search_schemas.OfferSearchRequest,
        rate_limit_timeout: float = 30,
    ) -> OffersResponseAdapter:
        response = await self._make_request(
            "POST",
            "/offers",
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return OffersResponseAdapter(
            response_offer_search_schemas.OfferSearchResponse.parse_raw(
                response.content,
            ),
        )

    async def get_offer(
        self,
        offer_id: UUID,
    ) -> response_priced_offer_schemas.PricedOfferResponse:
        response = await self._make_request(
            "GET",
            "/offers/{offer_id}".format(offer_id=offer_id),
        )

        return response_priced_offer_schemas.PricedOfferResponse.parse_raw(
            response.content,
        )

    async def create_order(
        self,
        request: request_order_schemas.CreateOrderRequest,
        rate_limit_timeout: float = 60,
    ) -> tuple[response_order_schemas.OrderResponse, bytes]:
        response = await self._make_request(
            "POST",
            "/orders",
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return (
            response_order_schemas.OrderResponse.parse_raw(
                response.content,
            ),
            response.content,
        )

    async def get_order(self, order_id: UUID) -> response_order_schemas.OrderResponse:
        response = await self._make_request(
            "GET",
            "/orders/{order_id}".format(order_id=order_id),
        )

        return response_order_schemas.OrderResponse.parse_raw(
            response.content,
        )

    async def cancel_order(self, order_id: UUID) -> None:
        await self._make_request(
            "DELETE",
            "/orders/{order_id}".format(order_id=order_id),
        )

    async def update_order(
        self,
        order_id: UUID,
        request: request_order_schemas.UpdateOrderRequest,
    ) -> response_order_schemas.OrderResponse:
        response = await self._make_request(
            "PATCH",
            "/orders/{order_id}".format(order_id=order_id),
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_order_schemas.OrderResponse.parse_raw(
            response.content,
        )

    async def passenger_name_correction(
        self,
        order_id: UUID,
        request: request_name_correction_schemas.NameCorrection,
    ) -> response_order_schemas.OrderResponse:
        response = await self._make_request(
            "POST",
            "/orders/{order_id}/name-correction".format(order_id=order_id),
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_order_schemas.OrderResponse.parse_raw(
            response.content,
        )

    async def get_services(
        self,
        offer_id: UUID | None = None,
        order_id: UUID | None = None,
    ) -> response_service_schemas.ServicesResponse:
        if offer_id is None and order_id is None:
            raise errors.BaNdcError(
                "one of [offerId, orderId] is required",
            )

        response = await self._make_request(
            "GET",
            "/services",
            _request_query_params(offer_id, order_id),
        )

        return response_service_schemas.ServicesResponse.parse_raw(
            response.content,
        )

    async def get_seats(
        self,
        offer_id: UUID | None = None,
        order_id: UUID | None = None,
    ) -> response_seat_schemas.SeatsResponse:
        if offer_id is None and order_id is None:
            raise errors.BaNdcError(
                "one of [offerId, orderId] is required",
            )

        response = await self._make_request(
            "GET",
            "/seats",
            _request_query_params(offer_id, order_id),
        )

        return response_seat_schemas.SeatsResponse.parse_raw(
            response.content,
        )

    async def add_seat(
        self,
        order_id: UUID,
        request: request_add_seat_schemas.AddSeats,
    ) -> response_order_schemas.OrderResponse:
        response = await self._make_request(
            "POST",
            "/orders/{order_id}/seats".format(order_id=order_id),
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_order_schemas.OrderResponse.parse_raw(
            response.content,
        )

    async def reshop(
        self,
        order_id: UUID,
        request: request_order_change_schemas.OrderReshopRequest,
    ) -> response_order_change_schemas.ReshopResponse:
        response = await self._make_request(
            "POST",
            "/orders/{order_id}/reshop".format(order_id=order_id),
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_order_change_schemas.ReshopResponse.parse_raw(
            response.content,
        )

    async def _make_request(
        self,
        method: str,
        path: str,
        query_params: Mapping[str, Any] | None = None,
        payload: Any | None = None,
        rate_limit_timeout: float = 60,
    ) -> httpx.Response:
        try:
            await asyncio.gather(
                *(
                    client.rate_limit(timeout=rate_limit_timeout)
                    for client in self._rate_limit_clients
                ),
            )
        except asyncio.TimeoutError as timeout_exc:
            raise errors.AsyncTimeOutError(inspect.getdoc(timeout_exc)) from timeout_exc

        try:
            response = await self._http_client.request(
                method=method,
                url=path,
                params=query_params,
                content=payload,
                headers={
                    "Authorization": "Bearer {0}".format(self._api_key),
                    "accept": "*/*",
                    "Content-type": "application/json",
                },
            )
        except httpx.HTTPError as raw_exc:
            raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError(
                errors.get_response_error_message(response),
            ) from exc

        return response
