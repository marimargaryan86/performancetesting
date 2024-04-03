import inspect
from collections.abc import Mapping
from json import dumps as json_dumps
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from snowfall.vendor.duffel import errors
from snowfall.vendor.duffel.builders.offer_request import OfferRequestData
from snowfall.vendor.duffel.builders.order_cancel import OrderCancelRequest
from snowfall.vendor.duffel.builders.order_request import OrderData
from snowfall.vendor.duffel.models import airport, common, webhook
from snowfall.vendor.duffel.models.base import (
    DuffelResponse,
    RemoteList,
    RemoteListPage,
)
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
        errors_response = ErrorResponse.model_validate_json(response.content)
    except ValidationError:
        return "can't parse error"

    error_status = str(errors_response.meta.status if errors_response.meta else "")
    error_title = errors_response.errors[0].title if errors_response.errors else ""
    error_message = errors_response.errors[0].message if errors_response.errors else ""
    return "{0}: {1}, {2}".format(error_status, error_title, error_message)


class DuffelClient:
    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        version: str,
        http_client: httpx.AsyncClient,
        rate_limit_client: RateLimitClient | None = None,
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
            payload=offer_request_data.model_dump_json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )

        return OfferRequestResponse.model_validate_json(response.content).response_data

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

        return SingleOfferResponse.model_validate_json(response.content).response_data

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

        return SeatResponse.model_validate_json(response.content).response_data

    async def order_request(
        self,
        order_data: OrderData,
        rate_limit_timeout: float = 60,
    ) -> tuple[Order, bytes]:
        response = await self._make_request(
            "POST",
            "/air/orders",
            payload=order_data.model_dump_json(
                exclude_none=True,
                exclude_unset=True,
                by_alias=True,
            ),
            rate_limit_timeout=rate_limit_timeout,
        )
        return (
            OrderResponse.model_validate_json(response.content).response_data,
            response.content,
        )

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

        return OrderResponse.model_validate_json(response.content).response_data

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

        return CancelResponse.model_validate_json(response.content).response_data

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

        return CancelResponse.model_validate_json(response.content).response_data

    # usage:
    # async for airport in self._client.list_airports(optional_filters):
    def list_airports(
        self,
        **kwargs: Any,  # filter
    ) -> RemoteList[common.Airport]:
        return RemoteList(
            lambda after=None: self.list_airports_page(after=after, **kwargs),
        )

    async def list_airports_page(
        self,
        **kwargs: Any,
    ) -> RemoteListPage[common.Airport]:
        response = await self._make_request(
            "GET",
            "air/airports",
            query_params=airport.AirportListRequest(**kwargs),
        )
        return RemoteListPage[common.Airport].model_validate(response.json())

    async def list_webhook_deliveries_page(
        self,
        **kwargs: Any,
    ) -> RemoteListPage[webhook.WebhookDelivery]:
        response = await self._make_request(
            "GET",
            "air/webhooks",
            query_params=webhook.WebhookDeliveryListRequest(**kwargs),
        )
        return RemoteListPage[webhook.WebhookDelivery].model_validate(response.json())

    def list_webhook_deliveries(
        self,
        **kwargs: Any,  # filter
    ) -> RemoteList[webhook.WebhookDelivery]:
        return RemoteList(
            lambda after=None: self.list_webhook_deliveries_page(after=after, **kwargs),
        )

    async def list_webhooks(self) -> RemoteListPage[webhook.Webhook]:
        response = await self._make_request("GET", "air/webhooks")
        return RemoteListPage[webhook.Webhook].model_validate(response.json())

    async def create_webhook(
        self,
        **kwargs: Any,
    ) -> webhook.WebhookCreateResponse:
        response = await self._make_request(
            "POST",
            "/air/webhooks",
            payload=webhook.WebhookCreateRequest(**kwargs),
        )

        response_model = DuffelResponse[webhook.WebhookCreateResponse].model_validate(
            response.json(),
        )
        return response_model.data

    async def ping_webhook(
        self,
        webhook_id: str,
    ) -> None:
        await self._make_request(
            "POST",
            "/air/webhooks/{webhook_id}/actions/ping".format(webhook_id=webhook_id),
        )

    async def delete_webhook(
        self,
        webhook_id: str,
        rate_limit_timeout: float = 60,
    ) -> bool:
        response = await self._make_request(
            "DELETE",
            "/air/webhooks/{webhook_id}".format(webhook_id=webhook_id),
            rate_limit_timeout=rate_limit_timeout,
        )
        return response.is_success

    async def _make_request(
        self,
        method: str,
        path: str,
        query_params: Mapping[str, Any] | BaseModel | None = None,
        payload: str | BaseModel | None = None,
        rate_limit_timeout: float = 60,
    ) -> httpx.Response:
        try:  # noqa: WPS229
            # check if GET query_params are a pydantic model,
            # and export them to dict if so
            if isinstance(query_params, BaseModel):
                query_params = query_params.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                    by_alias=True,
                )

            # check if POST payload is a pydantic model, and export it to json str if so
            if isinstance(payload, BaseModel):
                # mypy gets confused so I'm explicitly casting to string here
                payload = json_dumps(
                    {
                        "data": payload.dict(
                            exclude_none=True,
                            exclude_unset=True,
                            by_alias=True,
                        ),
                    },
                )

            if self._rate_limit_client:
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
        except (TimeoutError, httpx.HTTPError) as raw_exc:
            raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except (httpx.HTTPError, httpx.HTTPStatusError) as exc:
            raise errors.ServiceError(_get_response_error_message(response)) from exc

        return response
