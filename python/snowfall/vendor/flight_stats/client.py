import datetime

import httpx

from snowfall.stdlib.persistence.cache import async_cache_ttl
from snowfall.stdlib.transport.http import client
from snowfall.vendor.flight_stats.models import errors, flight_stats


class FlightStatsClient(client.HttpClient):
    def __init__(
        self,
        api_url: str,
        app_id: str,
        app_key: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(api_url, http_client)
        self._app_id = app_id
        self._app_key = app_key

    @async_cache_ttl(ttl=datetime.timedelta(minutes=10))
    async def get_flight_status(
        self,
        departure_at: datetime.date,
        carrier_code: str,
        flight_number: str,
    ) -> flight_stats.GetFlightStatusResponse:
        path = "{0}/{1}/dep/{2}/{3}/{4}".format(
            carrier_code,
            flight_number,
            departure_at.year,
            departure_at.month,
            departure_at.day,
        )
        query_parameters = {
            "appId": self._app_id,
            "appKey": self._app_key,
        }

        response = await self._make_request(
            options=client.RequestOptions(
                path=path,
                method="GET",
                query=query_parameters,
            ),
        )
        response_body = response.json()
        if "error" in response_body:
            exc = errors.FlightStatsError.from_error(
                flight_stats.Error.model_validate(response_body.get("error")),
            )
            raise exc
        return flight_stats.GetFlightStatusResponse(**response_body)
