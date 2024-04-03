import datetime
from collections.abc import Mapping
from typing import Any

import httpx


class FlightStatusClient:
    def __init__(
        self,
        api_url: str,
        app_id: str,
        app_key: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_url = api_url
        self._app_id = app_id
        self._app_key = app_key
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

    async def get_flight_status(
        self,
        departure_at: datetime.datetime,
        carrier: str,
        flight: str,
    ) -> dict[str, Any]:
        request_url = self._api_url + "{0}/{1}/dep/{2}/{3}/{4}".format(
            carrier,
            flight,
            departure_at.year,
            departure_at.month,
            departure_at.day,
        )
        return await self._make_request(
            method="GET",
            url=request_url,
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        query_parameters = {
            "appId": self._app_id,
            "appKey": self._app_key,
        }
        response = await self._client.request(
            method=method,
            url=url,
            params=query_parameters,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        response.raise_for_status()

        return response.json()
