from collections.abc import Sequence

import httpx

from snowfall.stdlib.persistence.cache import async_cache_ttl
from snowfall.stdlib.transport.http.client import HttpClient, RequestOptions
from snowfall.vendor.google_flights.models.emissions import (
    Flight,
    GetEmissionsResponse,
)


class Client(HttpClient):
    def __init__(
        self,
        base_url: str,
        key: str,
    ) -> None:
        self._key = key
        httpx_client = httpx.AsyncClient()
        httpx_client.headers.update(
            httpx.Headers(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            ),
        )
        super().__init__(base_url, httpx_client)

    @async_cache_ttl()
    async def get_emissions(
        self,
        flights: Sequence[Flight],
    ) -> GetEmissionsResponse:
        response = await self._make_request(
            options=RequestOptions(
                path="",
                method="POST",
                query={"key": self._key},
                payload={
                    "flights": [flight.model_dump(by_alias=True) for flight in flights],
                },
            ),
        )

        return GetEmissionsResponse(**response.json())
