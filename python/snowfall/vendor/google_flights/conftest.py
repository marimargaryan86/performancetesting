import httpx
import pytest

from snowfall.vendor.google_flights import co2_emissions


@pytest.fixture()
def httpx_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


@pytest.fixture()
def co2_emissions_client(
    httpx_client: httpx.AsyncClient,
) -> co2_emissions.Client:
    return co2_emissions.Client(
        base_url="https://test_url",
        key="key",
    )
