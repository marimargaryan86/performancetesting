import datetime
import json
import logging
import os
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

import httpx
import hvac
import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction.go.client import Client as GoClient

ALLURE_ENVIRONMENT_PROPERTIES_FILE = "environment.properties"
ALLUREDIR_OPTION = "--alluredir"
EXIT_MSG = "Exiting ; check your logs"
HTTPS_PREFIX = "https://"
HTTP_PREFIX = "http://"

logger = logging.getLogger()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API-TOKEN", action="store", help="api token to execute calls")
    parser.addoption("--ORIGIN", action="store", help="origin id")
    parser.addoption("--DESTINATION", action="store", help="destination id")
    parser.addoption("--DEPARTURE_AFTER", action="store", help="departure after")
    parser.addoption("--HOST", action="store", help="prod dev or any other host")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires environment",
    )


@pytest.fixture(scope="package")
def local_config(
    request: pytest.FixtureRequest,
) -> Mapping[str, str]:
    config_file_name = request.path.parent.name
    json_file_name = os.path.expanduser("~/{0}.json".format(config_file_name))
    if not os.path.exists(json_file_name):
        return {}
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
    local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    return request.config.getoption("API_TOKEN") or local_config.get("API_TOKEN") or ""


@pytest.fixture(scope="package", autouse=True)
def departure_after(departures_after: Sequence[str]) -> str:
    return departures_after[0]


@pytest.fixture(scope="package", autouse=True)
def departures_after(request: pytest.FixtureRequest) -> Sequence[str]:
    departures = request.config.getoption("DEPARTURE_AFTER")

    if not departures:
        departures = (
            datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        ).strftime("%Y-%m-%dT00:00:00.000Z")

    return departures.split(",")


@pytest.fixture(scope="package", autouse=True)
def origin(
    origins: Sequence[str],
) -> str:
    return origins[0]


@pytest.fixture(scope="package", autouse=True)
def origins(
    local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> Sequence[str]:
    origins = request.config.getoption("ORIGIN") or local_config.get("ORIGIN") or ""
    return origins.split(",")


@pytest.fixture(scope="package", autouse=True)
def destination(
    destinations: Sequence[str],
) -> str:
    return destinations[0]


@pytest.fixture(scope="package", autouse=True)
def destinations(
    local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> Sequence[str]:
    destinations = (
        request.config.getoption("DESTINATION")
        or local_config.get(
            "DESTINATION",
        )
        or ""
    )
    return destinations.split(",")


@pytest.fixture(scope="package")
def protocol(
    request: pytest.FixtureRequest,
    local_config: Mapping[str, str],
) -> str:
    return request.config.getoption("PROTOCOL") or local_config.get("PROTOCOL") or ""


@pytest.fixture(scope="package", autouse=True)
def host(
    request: pytest.FixtureRequest,
    local_config: Mapping[str, str],
) -> str:
    return request.config.getoption("HOST") or local_config.get("HOST") or ""


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


@pytest.fixture()
def junction_client(
    api_token: str,
    host: str,
) -> GoClient:
    api_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "junction_api_host"),
    )
    junction_api_token = get_variable_value(host, api_token, "junction_api_token")
    client_timeout = 20
    return GoClient(
        base_url=api_url,
        auth=auth.TokenAuth(junction_api_token),
        client=httpx.AsyncClient(timeout=client_timeout),
    )


@pytest.fixture()
def mobile_client(
    api_token: str,
    host: str,
) -> MobileApiClient:
    api_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "mobile_api_host"),
    )
    mobile_token = get_variable_value(host, api_token, "mobile_api_token")
    client_timeout = 20

    return MobileApiClient(
        base_url=api_url,
        auth=auth.TokenAuth(mobile_token),
        client=httpx.AsyncClient(timeout=client_timeout),
    )


@pytest.fixture()
def get_mongo_config(
    api_token: str,
    host: str,
) -> dict[str, Any]:
    mdb_user = get_variable_value(host, api_token, "mongodb_dev_user")
    mdb_password = get_variable_value(host, api_token, "mongodb_dev_password")
    mdb_server = get_variable_value(host, api_token, "mongodb_dev_server")
    mdb_port = get_variable_value(host, api_token, "mongodb_dev_port")

    return {
        "mongodb_dev_user": mdb_user,
        "mongodb_dev_password": mdb_password,
        "mongodb_dev_server": mdb_server,
        "mongodb_dev_port": mdb_port,
    }


def get_variable_value(
    host: str,
    api_token: str,
    variable_name: str,
) -> str:
    vusername, vpassword = api_token.split("+")
    client = hvac.Client(url=host)
    client.auth.userpass.login(username=vusername, password=vpassword)
    is_authenticated = client.is_authenticated()
    returned_data = {}
    if is_authenticated:
        returned_data = get_variable_from_server(client, "development")
        if not returned_data:
            returned_data = get_variable_from_server(client, "production")

    return str(returned_data["data"]["data"][variable_name])


def get_variable_from_server(
    client: hvac.Client,
    environment: str,
) -> dict[str, Any]:
    query = "kv/data/{e}/{s}".format(e=environment, s="api-automation")
    try:
        returned_data = client.read(query)
    except hvac.exceptions.Forbidden:
        returned_data = {}
    return returned_data


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
def _save_properties_to_allure_file(
    add_allure_environment_property: Callable[[str, Any], None],
    origins: Sequence[str],
    destinations: Sequence[str],
    departures_after: Sequence[str],
) -> None:
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
