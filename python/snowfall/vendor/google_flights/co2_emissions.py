import asyncio
from collections.abc import AsyncIterable, Sequence

import httpx

from snowfall.stdlib.persistence.cache import async_cache_ttl
from snowfall.stdlib.transport.http.client import HttpClient, RequestOptions
from snowfall.vendor.google_flights.models import emissions as emissions_models


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

    async def get_emissions(
        self,
        flights: Sequence[emissions_models.Flight],
    ) -> emissions_models.GetEmissionsResponse:
        emissions = await asyncio.gather(
            *[
                self._get_emission(flight)
                async for flight in sequence_to_async_iterable(flights)
            ],
        )

        return emissions_models.GetEmissionsResponse(
            flight_emissions=emissions,
        )

    @async_cache_ttl()
    async def _get_emission(
        self,
        flight: emissions_models.Flight,
    ) -> emissions_models.FlightEmission:
        response = await self._make_request(
            options=RequestOptions(
                path="",
                method="POST",
                query={"key": self._key},
                payload={
                    "flights": [flight.model_dump(by_alias=True)],
                },
            ),
        )
        response_model = emissions_models.GetEmissionsResponse(**response.json())

        return response_model.flight_emissions[0]


async def sequence_to_async_iterable(
    sequence: Sequence[emissions_models.Flight],
) -> AsyncIterable[emissions_models.Flight]:
    for item in sequence:
        yield item
