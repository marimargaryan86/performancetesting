import abc
from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


class Client(abc.ABC):
    @abc.abstractmethod
    async def create_monitoring_rule(
        self,
        booking: models_pb2.Booking,
        monitoring_rule_id: str,
    ) -> dict[str, Any]:
        """Set flight alert on flightstats-api."""


class DictClient(Client):
    def __init__(
        self,
    ) -> None:
        self._bookings: dict[str, models_pb2.Booking] = {}

    async def create_monitoring_rule(
        self,
        booking: models_pb2.Booking,
        monitoring_rule_id: str,
    ) -> dict[str, Any]:
        return {}


class FlightStatsClient(Client):
    def __init__(
        self,
        api_url: str,
        app_id: str,
        app_key: str,
        webhook_url: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_url = api_url
        self._app_id = app_id
        self._app_key = app_key
        self._webhook_url = webhook_url
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)

        self._client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/vnd.api+json",
                    "Content-Type": "application/vnd.api+json",
                },
            ),
        )

    async def create_monitoring_rule(
        self,
        booking: models_pb2.Booking,
        monitoring_rule_id: str,
    ) -> dict[str, Any]:
        air_booking = booking.value
        departure_at_datetime = protobuf.protobuf_to_datetime(air_booking.departure_at)
        request_url = (
            self._api_url
            + "/flex/alerts/rest/v1/json/create/"
            + "{0}/{1}/from/{2}/to/{3}/departing/{4}/{5}/{6}".format(
                air_booking.route_identifier.carrier,
                air_booking.route_identifier.flight_number,
                air_booking.origin_iata,
                air_booking.destination_iata,
                departure_at_datetime.year,
                departure_at_datetime.month,
                departure_at_datetime.day,
            )
        )
        query_parameters = {
            "name": "{0}{1}-{2}-{3}".format(
                air_booking.route_identifier.carrier,
                air_booking.route_identifier.flight_number,
                air_booking.destination_iata,
                air_booking.origin_iata,
            ),
            "events": "depGate,depDelay,bag,div",
            "deliverTo": self._webhook_url,
            "type": "JSON",
            "extendedOptions": "useHttpErrors",
            "_resource_id": monitoring_rule_id,
        }
        return await self._make_request(
            method="GET",
            url=request_url,
            query_parameters=query_parameters,
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        query_parameters: Mapping[str, Any],
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.request(
            method=method,
            url=url,
            params=query_parameters,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "appId": self._app_id,
                "appKey": self._app_key,
            },
        )
        response.raise_for_status()

        return response.json()
