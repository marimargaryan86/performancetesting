from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.karhoo import client


@pytest.fixture
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture
def karhoo_client(httpx_client: httpx.AsyncClient) -> client.KarhooClient:
    return client.KarhooClient(
        api_key="xxxx",
        base_url="https://test_url",
        http_client=httpx_client,
    )
