import datetime
import json
import logging
import os
from typing import Mapping, Sequence

import httpx
import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API-TOKEN", action="store", help="api token to execute calls")
    parser.addoption("--ORIGIN", action="store", help="origin id")
    parser.addoption("--DESTINATION", action="store", help="destination id")
    parser.addoption("--DEPARTURE_AFTER", action="store", help="departure after")
    parser.addoption("--PROTOCOL", action="store", help="protocol e.g. http or https")
    parser.addoption("--HOST", action="store", help="prod dev or any other host")


@pytest.fixture(scope="session")
def _local_config() -> Mapping[str, str]:
    json_file_name = os.path.expanduser("~/test_config.json")
    if not os.path.exists(json_file_name):
        return {}
    logging.info("Reading of local configuration...")
    with open(json_file_name) as json_file:
        return json.load(json_file)


@pytest.fixture(scope="session")
def api_token(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    return request.config.getoption("API_TOKEN") or _local_config.get("API_TOKEN") or ""


@pytest.fixture(scope="session")
def departure_after(request: pytest.FixtureRequest) -> str:
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return request.config.getoption("DEPARTURE_AFTER") or tomorrow.strftime(
        "%Y-%m-%dT00:00:00.000Z",
    )


@pytest.fixture(scope="session")
def origin(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("ORIGIN")


@pytest.fixture(scope="session")
def destination(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("DESTINATION")


@pytest.fixture(scope="session")
def protocol(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("PROTOCOL")


@pytest.fixture(scope="session")
def host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("HOST")


@pytest.fixture(scope="session")
def headers(api_token: str) -> dict[str, str]:
    return {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(api_token),
    }


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],  # noqa: WPS110
) -> None:
    if not config.getoption("-m"):
        skip_me = pytest.mark.skip(reason="use `-m integration` to run this test")
        for ii in items:
            if "integration" in ii.keywords:
                ii.add_marker(skip_me)


@pytest.fixture(scope="function")
def client(api_token: str, host: str) -> JunctionClient:
    return JunctionClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=10),
    )
