from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.save_a_train import client


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def save_a_train_client(httpx_client: httpx.AsyncClient) -> client.SATClient:
    return client.SATClient(
        email="test@snowfall.com",
        password="secret",
        password_search="secret",
        token="token",
        api_url="https://test_url",
        api_search_url="https://test_url/searches",
        api_search_timeout=10,
        api_search_requests_limit=1,
        client=httpx_client,
    )
