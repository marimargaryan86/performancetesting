import abc
from collections.abc import Mapping
from typing import Any

import httpx

from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_weather_forecast(
        self,
        location: models_pb2.Location,
    ) -> dict[str, Any]:
        """Get weather forecast for location."""


class DictClient(Client):
    def __init__(
        self,
    ) -> None:
        self._bookings: dict[str, models_pb2.Booking] = {}

    async def get_weather_forecast(
        self,
        location: models_pb2.Location,
    ) -> dict[str, Any]:
        return {}


class OpenWeatherMapClient(Client):
    def __init__(  # noqa: WPS211
        self,
        api_url: str,
        api_key: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_url = api_url
        self._api_key = api_key
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)

    async def get_weather_forecast(
        self,
        location: models_pb2.Location,
    ) -> dict[str, Any]:
        query_parameters = {
            "lat": location.coordinates.latitude,
            "lon": location.coordinates.longitude,
            "appid": self._api_key,
            "units": "metric",
        }
        return await self._make_request(
            method="GET",
            url=self._api_url,
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
            },
        )
        response.raise_for_status()

        return response.json()
