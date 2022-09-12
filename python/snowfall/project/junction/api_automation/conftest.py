from typing import Any

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API-TOKEN", action="store", help="api token to execute calls")
    parser.addoption("--ORIGIN", action="store", help="origin id")
    parser.addoption("--DESTINATION", action="store", help="destination id")
    parser.addoption("--DEPARTURE_AFTER", action="store", help="departure after")
    parser.addoption("--PROTOCOL", action="store", help="protocol e.g. http or https")
    parser.addoption("--HOST", action="store", help="prod dev or any other host")


@pytest.fixture(scope="session")
def api_token(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("API_TOKEN")


@pytest.fixture(scope="session")
def departure_after(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("DEPARTURE_AFTER")


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


def pytest_collection_modifyitems(config: pytest.Config, items: Any) -> None:
    if not config.getoption("-m"):
        skip_me = pytest.mark.skip(reason="use `-m integration` to run this test")
        for ii in items:
            if "integration" in ii.keywords:
                ii.add_marker(skip_me)
