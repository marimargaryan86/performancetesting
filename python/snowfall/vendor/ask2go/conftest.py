from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.ask2go import client


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def ask2go_client(http_client: httpx.AsyncClient) -> client.Ask2GoClient:
    return client.Ask2GoClient(
        api_base_url="https://test_url",
        api_booking_base_url="https://test_url",
        http_client=http_client,
    )
