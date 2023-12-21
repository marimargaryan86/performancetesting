from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.flight_stats import client


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def flight_stats_client(httpx_client: httpx.AsyncClient) -> client.FlightStatsCilent:
    return client.FlightStatsCilent(
        api_url="https://test_url",
        app_id="app_id",
        app_key="app_key",
        http_client=httpx_client,
    )
