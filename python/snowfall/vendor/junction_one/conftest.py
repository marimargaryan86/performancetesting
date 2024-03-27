from collections.abc import AsyncIterator, Sequence
from typing import Any

import aiofiles
import httpx
import orjson
import pytest

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.junction_one.auth import (
    JunctionOneAuth,
    TokenAuth,
)
from snowfall.vendor.junction_one.client import (
    JunctionOneClient,
)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires environment",
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API_KEY", action="store", help="api key")
    parser.addoption("--AUTHORIZATION", action="store", help="api key")


@pytest.fixture(scope="package", autouse=True)
def api_key(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("API_KEY")


@pytest.fixture(scope="package", autouse=True)
def authorization(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("AUTHORIZATION")


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    if not config.getoption("-m"):
        skip_marker = pytest.mark.skip(reason="use `-m integration` to run this")
        for test_item in items:
            if "integration" in test_item.keywords:
                test_item.add_marker(skip_marker)


async def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.junction_one.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    async with aiofiles.open(file_path) as json_file:
        return orjson.loads(await json_file.read())


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def junction_one_client(http_client: httpx.AsyncClient) -> JunctionOneClient:
    return JunctionOneClient(api_base_url="https://localhost/", http_client=http_client)


@pytest.fixture()
def remote_junction_one_client(
    api_key: str,
    authorization: str,
    http_client: httpx.AsyncClient,
) -> JunctionOneClient:
    return JunctionOneClient(
        api_base_url="https://one.junction.dev/",
        http_client=http_client,
        auth=TokenAuth(
            JunctionOneAuth(
                api_key=api_key,
                authorization=authorization,
            ),
        ),
    )
