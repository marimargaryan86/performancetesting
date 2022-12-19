import datetime
import json
import logging
import os
from typing import Any, Callable, Iterator, Mapping, Sequence

import httpx
import pytest

from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.junction.client import JunctionClient, MobileApiClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

ALLURE_ENVIRONMENT_PROPERTIES_FILE = "environment.properties"
ALLUREDIR_OPTION = "--alluredir"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API-TOKEN", action="store", help="api token to execute calls")
    parser.addoption("--ORIGIN", action="store", help="origin id")
    parser.addoption("--DESTINATION", action="store", help="destination id")
    parser.addoption("--DEPARTURE_AFTER", action="store", help="departure after")
    parser.addoption("--PROTOCOL", action="store", help="protocol e.g. http or https")
    parser.addoption("--HOST", action="store", help="prod dev or any other host")


@pytest.fixture(scope="package")
def _local_config(
    request: pytest.FixtureRequest,
) -> Mapping[str, str]:
    config_file_name = request.path.parent.name
    json_file_name = os.path.expanduser("~/{0}.json".format(config_file_name))
    if not os.path.exists(json_file_name):
        return {}
    logging.debug("Reading of local config from {0}.json ...", config_file_name)
    with open(json_file_name) as json_file:
        config = json.load(json_file)
        malformed_keys = [
            key
            for key in config
            if any(not (char.isupper() or char == "_") for char in key)
        ]
        if malformed_keys:
            raise ValueError("Bad config keys: {0}".format(malformed_keys))
        return config


@pytest.fixture(scope="package")
def api_token(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    return request.config.getoption("API_TOKEN") or _local_config.get("API_TOKEN") or ""


@pytest.fixture(scope="package", autouse=True)
def departure_after(request: pytest.FixtureRequest) -> str:
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    departures_table = request.config.getoption("DEPARTURE_AFTER") or tomorrow.strftime(
        "%Y-%m-%dT00:00:00.000Z",
    )
    departures = departures_table.split(",")
    return departures[0]


@pytest.fixture(scope="package", autouse=True)
def origin(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    origin = request.config.getoption("ORIGIN") or _local_config.get("ORIGIN") or ""
    origin_table = origin.split(",")
    return origin_table[0]


@pytest.fixture(scope="package", autouse=True)
def origins(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> Sequence[str]:
    origins = request.config.getoption("ORIGIN") or _local_config.get("ORIGIN") or ""
    return origins.split(",")


@pytest.fixture(scope="package", autouse=True)
def destination(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    destination = (
        request.config.getoption("DESTINATION")
        or _local_config.get("DESTINATION")
        or ""
    )
    destination_table = destination.split(",")
    return destination_table[0]


@pytest.fixture(scope="package", autouse=True)
def destinations(
    _local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> Sequence[str]:
    destinations = (
        request.config.getoption("DESTINATION")
        or _local_config.get(
            "DESTINATION",
        )
        or ""
    )
    return destinations.split(",")


@pytest.fixture(scope="package")
def protocol(
    request: pytest.FixtureRequest,
    _local_config: Mapping[str, str],
) -> str:
    return request.config.getoption("PROTOCOL") or _local_config.get("PROTOCOL") or ""


@pytest.fixture(scope="package", autouse=True)
def host(
    request: pytest.FixtureRequest,
    _local_config: Mapping[str, str],
) -> str:
    return request.config.getoption("HOST") or _local_config.get("HOST") or ""


@pytest.fixture(scope="package")
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
def junction_client(
    api_token: str,
    host: str,
) -> JunctionClient:
    client_timeout = 20
    return JunctionClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=client_timeout),
    )


@pytest.fixture(scope="function")
def mobile_client(
    api_token: str,
    host: str,
) -> MobileApiClient:
    client_timeout = 20
    return MobileApiClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=client_timeout),
    )


@pytest.fixture(scope="function")
def api_layer_client(
    api_token: str,
    host: str,
) -> APILayer:
    client_timeout = 20.0
    return APILayer(
        base_url="https://{0}".format(host),
        api_key=api_token,
        timeout=client_timeout,
    )


@pytest.fixture(scope="session", autouse=True)
def add_allure_environment_property(
    request: pytest.FixtureRequest,
) -> Iterator[Callable[[str, Any], None]]:
    environment_properties = {}

    def maker(key: str, key_value: Any) -> None:  # noqa: WPS430
        environment_properties.update({key: key_value})

    yield maker

    if not request.config.getoption(ALLUREDIR_OPTION):
        return

    if not os.path.isdir(request.config.getoption(ALLUREDIR_OPTION)):
        return

    if not environment_properties:
        return

    with open(
        os.path.join(
            request.config.getoption(ALLUREDIR_OPTION),
            ALLURE_ENVIRONMENT_PROPERTIES_FILE,
        ),
        "w",
    ) as file_name:
        file_data = "\n".join(
            [
                "{0}={1}".format(env_variable, env_value)
                for env_variable, env_value in environment_properties.items()
            ],
        )
        file_name.write(file_data)


@pytest.fixture(autouse=True)
def save_properties_to_allure_file(
    add_allure_environment_property: Callable[[str, Any], None],
    origins: Sequence[str],
    destinations: Sequence[str],
    departures_after: Sequence[str],
    host: str,
) -> None:
    add_allure_environment_property(
        "host",
        host,
    )
    add_allure_environment_property(
        "origin",
        origins[0],
    )
    add_allure_environment_property(
        "destination",
        destinations[0],
    )
    add_allure_environment_property(
        "departure_after",
        departures_after[0],
    )
    add_allure_environment_property(
        "origins",
        origins,
    )
    add_allure_environment_property(
        "destinations",
        destinations,
    )
    add_allure_environment_property(
        "departures_after",
        departures_after,
    )
