from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.stdlib.transport.http import client


@pytest.fixture
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture
def http_client(httpx_client: httpx.AsyncClient) -> client.HttpClient:
    return client.HttpClient(
        base_url="https://test_url",
        http_client=httpx_client,
    )
