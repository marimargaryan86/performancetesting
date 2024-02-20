from collections.abc import AsyncIterator

import httpx
import pytest

from snowfall.vendor.direct_ferries import client
from snowfall.vendor.direct_ferries.clients import auth, base


@pytest.fixture()
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def direct_ferries_client(httpx_client: httpx.AsyncClient) -> client.DfHttpClient:
    return client.DfHttpClient(
        http_client=httpx_client,
        auth_client=auth.AuthClient(
            api_url="http://localhost",
            client_secret="mock_client_secret",
            client_id="mock_client_id",
            http_client=httpx_client,
        ),
        config=base.ClientConfig(
            api_url="http://localhost",
            partner_code="mock_partner_id",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            timeout=30,
        ),
    )
