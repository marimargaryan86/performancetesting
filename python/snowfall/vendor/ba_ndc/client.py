import inspect
from typing import Any, Mapping, Optional
from uuid import UUID

import httpx

from snowfall.vendor.ba_ndc import errors
from snowfall.vendor.ba_ndc.models import (
    request_offer_search_schemas,
    request_order_schemas,
    response_offer_search_schemas,
    response_order_schemas,
    response_priced_offer_schemas,
)


class BaNdcClient(object):
    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._api_base_url = httpx.URL(api_base_url).copy_with(path="/v2")
        self._api_key = api_key
        self._http_client = http_client
        self._http_client.base_url = self._api_base_url

    async def get_offers(
        self,
        request: request_offer_search_schemas.OfferSearchRequest,
    ) -> response_offer_search_schemas.OfferSearchResponse:
        response = await self._make_request(
            "POST",
            "/offers",
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_offer_search_schemas.OfferSearchResponse.parse_raw(
            response.content,
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
    ) -> response_order_schemas.OrderResponse:
        response = await self._make_request(
            "POST",
            "/orders",
            payload=request.json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
        )

        return response_order_schemas.OrderResponse.parse_raw(
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

    async def _make_request(
        self,
        method: str,
        path: str,
        query_params: Optional[Mapping[str, Any]] = None,
        payload: Optional[Any] = None,
    ) -> httpx.Response:
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
