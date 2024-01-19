import httpx
import pytest

from snowfall.vendor.fluxir import client


@pytest.fixture()
def httpx_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture()
def auth() -> client.FluxirAuth:
    return client.FluxirAuth(
        base_url="https://test_url",
        username="username",
        password="password",
        tenant_id="tenant_id",
    )


@pytest.fixture()
def fluxir_client(
    httpx_client: httpx.AsyncClient,
    auth: client.FluxirAuth,
) -> client.FluxirClient:
    return client.FluxirClient(
        base_url="https://test_url",
        auth=auth,
        tenant_id="tenant_id",
        client=httpx_client,
    )
