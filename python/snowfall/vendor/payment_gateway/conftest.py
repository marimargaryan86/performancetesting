from collections.abc import AsyncIterator, Sequence

import httpx
import pytest

from snowfall.vendor.payment_gateway.client import PayGwClient


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires environment",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    if not config.getoption("-m"):
        skip_marker = pytest.mark.skip(reason="use `-m integration` to run this")
        for test_item in items:
            if "integration" in test_item.keywords:
                test_item.add_marker(skip_marker)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--ORYSESSION", action="store", help="ory session key")
    parser.addoption("--J1USER", action="store", help="j1 user id")
    parser.addoption("--J1SESSION", action="store", help="j1 session token")
    parser.addoption("--PAYURL", action="store", help="pay gateway url")


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def ory_session(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("ORYSESSION")


@pytest.fixture()
def pay_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("PAYURL") or "https://payment-gw.junction.dev/"


@pytest.fixture()
def j1_user(request: pytest.FixtureRequest) -> int:
    return int(request.config.getoption("J1USER"))


@pytest.fixture()
def j1_session(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("J1SESSION")


@pytest.fixture()
def pay_gw_client(
    http_client: httpx.AsyncClient,
    pay_url: str,
    ory_session: str,
) -> PayGwClient:
    return PayGwClient(
        api_base_url=pay_url,
        http_client=http_client,
        ory_session=ory_session,
    )
