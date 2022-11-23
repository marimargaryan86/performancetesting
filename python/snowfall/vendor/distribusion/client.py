import contextlib
import http
import inspect
import json
from typing import Any, Mapping, Optional

import httpx

from snowfall.vendor.distribusion import errors, jsonapi_helpers
from snowfall.vendor.distribusion.models import (
    bookings,
    connections,
    criterias,
    marketing_carriers,
    orders,
    stations,
)


def _get_response_error_message(response: httpx.Response) -> str:
    status = http.HTTPStatus(response.status_code)
    description = status.description

    with contextlib.suppress(json.decoder.JSONDecodeError, AttributeError):
        description = response.json().get("title") or status.description

    return "{0}: {1}".format(status.value, description)


class DistribusionClient(object):  # noqa: WPS214
    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        retailer_partner_number: str,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._api_base_url = httpx.URL(api_base_url).copy_with(path="/retailers/v4")
        self._api_key = api_key
        self._retailer_partner_number = retailer_partner_number
        self._http_client = http_client
        self._http_client.base_url = self._api_base_url

    async def get_marketing_carriers(self) -> list[marketing_carriers.MarketingCarrier]:
        response = await self._make_request(
            "GET",
            "/marketing_carriers",
        )

        return [
            marketing_carriers.MarketingCarrier(**carrier)
            for carrier in jsonapi_helpers.flatten_list(response.json())
        ]

    async def get_marketing_carrier_details(
        self,
        marketing_carrier_id: str,
    ) -> marketing_carriers.MarketingCarrierDetails:
        response = await self._make_request(
            "GET",
            "/marketing_carriers/{marketing_carrier_id}".format(
                marketing_carrier_id=marketing_carrier_id,
            ),
            query_params={"locale": "en", "currency": "EUR"},
        )

        return marketing_carriers.MarketingCarrierDetails(
            **jsonapi_helpers.flatten_object(response.json()),
        )

    async def get_stations(self) -> list[stations.Station]:
        response = await self._make_request(
            "GET",
            "/stations",
            query_params={"locale": "en"},
        )

        return [
            stations.Station(**station)
            for station in jsonapi_helpers.flatten_list(response.json())
        ]

    async def get_marketing_carrier_stations(
        self,
        marketing_carrier_id: str,
    ) -> list[stations.StationId]:
        url = "/marketing_carriers/{marketing_carrier_id}/stations"
        response = await self._make_request(
            "GET",
            path=url.format(marketing_carrier_id=marketing_carrier_id),
        )

        return [
            stations.StationId(**station)
            for station in jsonapi_helpers.flatten_list(response.json())
        ]

    async def get_booking_by_id(
        self,
        booking_id: str,
    ) -> bookings.Booking:
        url = "/bookings/{booking_id}"
        response = await self._make_request(
            "GET",
            path=url.format(booking_id=booking_id),
        )

        return bookings.Booking(**jsonapi_helpers.flatten_object(response.json()))

    async def find_connections(
        self,
        criteria: criterias.FindConnectionsCriteria,
    ) -> list[connections.Connection]:
        response = await self._make_request(
            "GET",
            "/connections/find",
            query_params={
                "locale": criteria.locale,
                "departure_stations[]": criteria.departure_stations,
                "arrival_stations[]": criteria.arrival_stations,
                "departure_date": criteria.departure_date.isoformat(),
                "pax": criteria.pax,
                "currency": criteria.currency,
            },
        )

        return [
            connections.Connection(**connection)
            for connection in jsonapi_helpers.flatten_list(response.json())
        ]

    async def get_connected_stations(
        self,
        criteria: criterias.ConnectedStationsCriteria,
    ) -> list[connections.Connection]:
        query_params = dict[str, Any]()

        if criteria.page_size:
            query_params["page[size]"] = criteria.page_size

        if criteria.next_page:
            query_params["page[after]"] = criteria.next_page

        if criteria.carrier_code:
            query_params["filter[marketing_carrier_codes][]"] = criteria.carrier_code

        response = await self._make_request(
            "GET",
            "/connected_stations",
            query_params,
        )

        return [
            connections.Connection(**connection)
            for connection in jsonapi_helpers.flatten_list(response.json())
        ]

    async def get_connection_vacancy(
        self,
        criteria: criterias.ConnectionVacancyCriteria,
    ) -> connections.ConnectionVacancy:
        query_params = {
            "marketing_carrier": criteria.marketing_carrier,
            "departure_station": criteria.departure_station,
            "arrival_station": criteria.arrival_station,
            "departure_time": criteria.departure_time.isoformat(timespec="minutes"),
            "arrival_time": criteria.arrival_time.isoformat(timespec="minutes"),
            "passengers[][pax]": criteria.pax,
            "passengers[][type]": criteria.passenger_type,
            "currency": criteria.currency,
        }

        if criteria.fare_class:
            query_params["fare_class"] = criteria.fare_class

        if criteria.return_departure_time and criteria.return_arrival_time:
            query_params[
                "return_departure_time"
            ] = criteria.return_departure_time.isoformat(timespec="minutes")
            query_params[
                "return_arrival_time"
            ] = criteria.return_arrival_time.isoformat(timespec="minutes")

        response = await self._make_request(
            "GET",
            "/connections/vacancy",
            query_params,
        )

        return connections.ConnectionVacancy(
            **jsonapi_helpers.flatten_object(response.json()),
        )

    async def get_connection_seats(
        self,
        criteria: criterias.ConnectionSeats,
    ) -> list[connections.ConnectionSeat]:
        response = await self._make_request(
            "GET",
            "/connections/seats",
            query_params={
                "marketing_carrier": criteria.marketing_carrier,
                "departure_station": criteria.departure_station,
                "arrival_station": criteria.arrival_station,
                "departure_time": criteria.departure_time.isoformat(timespec="minutes"),
                "arrival_time": criteria.arrival_time.isoformat(timespec="minutes"),
            },
        )

        return [
            connections.ConnectionSeat(**seat)
            for seat in jsonapi_helpers.flatten_list(response.json())
        ]

    async def create_order(
        self,
        criteria: criterias.CreateOrder,
    ) -> orders.OrderCreateResponse:
        response = await self._make_request(
            "POST",
            "/orders/create",
            payload={
                "marketing_carrier": criteria.marketing_carrier,
                "departure_station": criteria.departure_station,
                "arrival_station": criteria.arrival_station,
                "departure_time": criteria.departure_time,
                "arrival_time": criteria.arrival_time,
                "retailer_partner_number": self._retailer_partner_number,
                "title": criteria.title,
                "first_name": criteria.first_name,
                "last_name": criteria.last_name,
                "email": criteria.email,
                "phone": criteria.phone,
                "city": criteria.city,
                "zip_code": criteria.zip_code,
                "street_and_number": criteria.street_and_number,
                "execute_payment": criteria.execute_payment,
                "payment_method": criteria.payment_method.value,
                "total_price": criteria.total_price,
                "pax": criteria.pax,
                "terms_accepted": criteria.terms_accepted,
                "locale": criteria.locale,
                "currency": criteria.currency,
                "send_customer_email": criteria.send_customer_email,
                "fare_class": criteria.fare_class,
                "passengers": [
                    {
                        "first_name": passenger.first_name,
                        "last_name": passenger.last_name,
                        "type": passenger.passenger_type,
                    }
                    for passenger in criteria.passengers
                ],
            },
        )

        return orders.OrderCreateResponse(
            **jsonapi_helpers.flatten_object(response.json()),
        )

    async def get_order(self, order_id: str) -> orders.OrderResponse:
        response = await self._make_request(
            "GET",
            "/orders/{order_id}".format(order_id=order_id),
        )

        return orders.OrderResponse(**jsonapi_helpers.flatten_object(response.json()))

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
                json=payload,
                headers={"Api-Key": self._api_key, "accept": "application/json"},
            )
        except httpx.HTTPError as raw_exc:
            raise errors.ServiceError(inspect.getdoc(raw_exc)) from raw_exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise errors.ServiceError(_get_response_error_message(response)) from exc

        return response
