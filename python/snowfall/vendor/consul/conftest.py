from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.consul import client


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def consul_client(httpx_client: httpx.AsyncClient) -> client.ConsulClient:
    return client.ConsulClient(
        api_base_url="https://test_url",
        api_token="xxxx",
        httpx_client=httpx_client,
        version="v1",
    )
