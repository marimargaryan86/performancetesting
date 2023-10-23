import datetime
import json
import logging
from collections.abc import Callable, Iterator, Mapping, Sequence
from itertools import starmap
from pathlib import Path
from typing import Any

import httpx
import hvac
import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.stdlib.transport.http import auth

ALLURE_ENVIRONMENT_PROPERTIES_FILE = "environment.properties"
ALLUREDIR_OPTION = "--alluredir"
EXIT_MSG = "Exiting ; check your logs"
HTTPS_PREFIX = "https://"
HTTP_PREFIX = "http://"

logger = logging.getLogger()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--API-TOKEN", action="store", help="api token to execute calls")
    parser.addoption("--DEPARTURE_AFTER", action="store", help="departure after")
    parser.addoption("--HOST", action="store", help="prod dev or any other host")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires environment",
    )
    config.addinivalue_line(
        "markers",
        "smoke: smoke test that requires environment",
    )


@pytest.fixture(scope="package")
def local_config(
    request: pytest.FixtureRequest,
) -> Mapping[str, str]:
    config_file_name = request.path.parent.name
    json_file_name = (Path.home() / config_file_name).with_suffix(".json")
    if not json_file_name.exists():
        return {}
    with json_file_name.open() as json_file:
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


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    if not config.getoption("-m"):
        skip_integration = pytest.mark.skip(
            reason="use `-m integration` to run this test",
        )
        for i_integration in items:
            if "integration" in i_integration.keywords:
                i_integration.add_marker(skip_integration)
        skip_smoke = pytest.mark.skip(reason="use `-m smoke` to run this test")
        for i_smoke in items:
            if "smoke" in i_smoke.keywords:
                i_smoke.add_marker(skip_smoke)


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
        returned_data = get_variable_from_server(client, "sandbox")
        if not returned_data:
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

    allure_dir = request.config.getoption(ALLUREDIR_OPTION)
    allure_dir_path = Path(allure_dir)
    if not allure_dir_path.is_dir():
        return

    if not environment_properties:
        return

    allure_env_file = allure_dir_path / ALLURE_ENVIRONMENT_PROPERTIES_FILE
    file_data = "\n".join(
        list(starmap("{0}={1}".format, environment_properties.items())),
    )
    allure_env_file.write_text(file_data)


@pytest.fixture(autouse=True)
def _save_properties_to_allure_file(
    add_allure_environment_property: Callable[[str, Any], None],
    departures_after: Sequence[str],
) -> None:
    add_allure_environment_property(
        "departure_after",
        departures_after[0],
    )
    add_allure_environment_property(
        "departures_after",
        departures_after,
    )
