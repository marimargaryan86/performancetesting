import datetime
import json
import logging
import re
from collections.abc import (
    AsyncGenerator,
    Callable,
    Generator,
    Iterator,
    Mapping,
    Sequence,
)
from itertools import starmap
from pathlib import Path
from typing import Any

import allure
import httpx
import hvac
import pytest
from pymongo import MongoClient

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)
from snowfall.project.junction.api_automation.test_functions.helper import (
    ConfigurationManager,
    get_variable_from_server,
    get_variable_value,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.stdlib import string
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
    parser.addoption("--BASIC_TOKEN", action="store", help="token to use with ORY")
    parser.addoption("--ORY_URL", action="store", help="url to get access token")
    parser.addoption("--LOCAL_API_URL", action="store", help="url to run locally")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: integration test that requires environment",
    )
    config.addinivalue_line(
        "markers",
        "smoke: smoke test that requires environment",
    )
    config.addinivalue_line(
        "markers",
        "verify: verifier test that requires environment",
    )
    config.addinivalue_line(
        "markers",
        "manually: only by manually execution",
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


@pytest.fixture(scope="package", autouse=True)
def api_token(
    local_config: Mapping[str, str],
    request: pytest.FixtureRequest,
) -> str:
    return request.config.getoption("API_TOKEN") or local_config.get("API_TOKEN") or ""


@pytest.fixture(scope="package", autouse=True)
def departure_after(departures_after: Sequence[str]) -> str:
    return departures_after[0]


@pytest.fixture(scope="package", autouse=True)
def departure_before(departures_before: Sequence[str]) -> str:
    return departures_before[0]


@pytest.fixture(scope="package", autouse=True)
def departures_after(request: pytest.FixtureRequest) -> Sequence[str]:
    departures = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT08:00:00.000Z")
    return departures.split(",")


@pytest.fixture(scope="package", autouse=True)
def departures_before(request: pytest.FixtureRequest) -> Sequence[str]:
    departures = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT10:00:00.000Z")
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


@pytest.fixture()
def stripe_api_key(
    api_token: str,
    host: str,
) -> str:
    return get_variable_value(host, api_token, "stripe_api_key")


@pytest.fixture()
def sentry_url(
    api_token: str,
    host: str,
) -> str:
    return get_variable_value(host, api_token, "sentry_url")


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    test_markers = [
        ("integration", "use `-m integration` to run this test"),
        ("smoke", "use `-m smoke` to run this test"),
        ("verify", "use `-m verify` to run this test"),
        ("manually", "use `-m manually` to run this test"),
    ]

    for marker, skip_reason in test_markers:
        if not config.getoption("-m"):
            skip_marker = pytest.mark.skip(reason=skip_reason)
            for test_item in items:
                if marker in test_item.keywords:
                    test_item.add_marker(skip_marker)


@pytest.fixture()
def mobile_client(
    api_token: str,
    host: str,
    sentry_url: str,
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
        token=mobile_token,
        client=httpx.AsyncClient(timeout=client_timeout),
        sentry_url=sentry_url,
    )


@pytest.fixture()
def mock_mobile_client(
    api_token: str,
    host: str,
    sentry_url: str,
) -> MobileApiClient:
    api_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "mock_mobile_api_host"),
    )
    mobile_token = get_variable_value(host, api_token, "mock_mobile_api_token")
    client_timeout = 20

    return MobileApiClient(
        base_url=api_url,
        auth=auth.TokenAuth(mobile_token),
        token=mobile_token,
        client=httpx.AsyncClient(timeout=client_timeout),
        sentry_url=sentry_url,
    )


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
    departures_before: Sequence[str],
) -> None:
    add_allure_environment_property(
        "departure_after",
        departures_after[0],
    )
    add_allure_environment_property(
        "departures_after",
        departures_after,
    )
    add_allure_environment_property(
        "departures_before",
        departures_before,
    )


@pytest.fixture(autouse=True)
def _generate_sentry_url(
    sentry_url: str,
) -> Generator[None, None, None]:
    while logger.hasHandlers():
        logger.handlers[0].close()
        logger.removeHandler(logger.handlers[0])
    fh = logging.FileHandler("{0}.log".format(string.uuid()))
    tmp_log_file = fh.baseFilename
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    yield
    if logger.root.hasHandlers():
        logfile_path = Path(tmp_log_file)
        with logfile_path.open() as log_file:
            log_history = log_file.read().split("\n")
            x_request_id_logs = [
                re.search("(b'X-Request-Id', b'(.+?)')", log_line)
                for log_line in log_history
                if "X-Request-Id" in log_line
            ]
            trace_ids = [
                x_request_id.group(2)
                for x_request_id in x_request_id_logs
                if x_request_id
            ]
        if trace_ids:
            allure.attach(
                "{0}?query=trace%3A%5B{1}%5D".format(
                    sentry_url,
                    "%2C".join(trace_ids),
                ),
                "Sentry for all trace IDs",
            )


@pytest.fixture()
async def mobile_hub_client(
    api_token: str,
    host: str,
) -> AsyncGenerator[MobileApiClient, None]:
    api_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "mobile_api_hub_host"),
    )
    mobile_token = get_variable_value(host, api_token, "mobile_api_hub_token")
    client_timeout = 20
    headers = {
        "Cookie": "ory_kratos_session={0}".format(mobile_token),
    }
    async with httpx.AsyncClient(timeout=client_timeout, headers=headers) as client:
        yield MobileApiClient(
            base_url=api_url,
            auth=None,
            token=None,
            client=client,
        )


@pytest.fixture()
def mongo_client(host: str, api_token: str) -> MongoClient[Any]:
    mdb_user = get_variable_value(host, api_token, "mongodb_dev_user")
    mdb_password = get_variable_value(host, api_token, "mongodb_dev_password")
    mdb_server = get_variable_value(host, api_token, "mongodb_dev_server")
    mdb_port = get_variable_value(host, api_token, "mongodb_dev_port")

    mongo_uri = "mongodb://{0}:{1}@{2}:{3}/".format(
        mdb_user,
        mdb_password,
        mdb_server,
        mdb_port,
    )
    return MongoClient(mongo_uri)


@pytest.fixture()
def config_manager(host: str, api_token: str) -> ConfigurationManager:
    return ConfigurationManager(host, api_token)


def get_all_variable_values(host: str, api_token: str) -> dict[str, Any]:
    vault_username, vault_password = api_token.split("+")
    client = hvac.Client(url=host)
    client.auth.userpass.login(username=vault_username, password=vault_password)
    is_authenticated = client.is_authenticated()

    if not is_authenticated:
        return {}

    environments = ["sandbox", "development", "production"]
    for environment in environments:
        returned_data = get_variable_from_server(client, environment)
        if returned_data:
            return returned_data["data"]["data"]
    return {}


@pytest.fixture(scope="package")
@allure.title("Get variables from vault")  # type: ignore[misc]
def config_variables(host: str, api_token: str) -> dict[str, Any]:
    return get_all_variable_values(host=host, api_token=api_token)


def create_qa_client(api_url: str, api_token: str, sentry_url: str) -> QaClient:
    client_timeout = 20
    return QaClient(
        base_url=api_url,
        auth=auth.TokenAuth(api_token),
        token=api_token,
        client=httpx.AsyncClient(timeout=client_timeout),
        sentry_url=sentry_url,
    )


@pytest.fixture(scope="session", autouse=True)
def basic_token(request: pytest.FixtureRequest) -> str:
    return request.config.getoption(name="BASIC_TOKEN")


@pytest.fixture(scope="session", autouse=True)
def ory_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption(name="ORY_URL")


@pytest.fixture(scope="session", autouse=True)
def local_api_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption(name="LOCAL_API_URL")


async def get_access_token_from_ory(
    ory_url: str,
    basic_token: str,
) -> str:
    async with httpx.AsyncClient() as http_client:
        request = await http_client.post(
            ory_url,
            headers={"Authorization": "Basic {0}".format(basic_token)},
            data={"grant_type": "client_credentials"},
        )
    return request.json()["access_token"]


@pytest.fixture()
@allure.title("Instantiate a test client for Junction API")  # type: ignore[misc]
async def qa_client(
    config_variables: Mapping[str, str],
    sentry_url: str,
    basic_token: str,
    ory_url: str,
    local_api_url: str,
) -> QaClient:
    url_part = local_api_url if local_api_url else config_variables["rocket_api_host"]

    api_url = "{0}{1}".format(HTTPS_PREFIX, url_part)
    if basic_token and ory_url:
        access_token = await get_access_token_from_ory(
            ory_url=ory_url,
            basic_token=basic_token,
        )
    else:
        access_token = config_variables["rocket_api_token_mock"]
    return create_qa_client(api_url, access_token, sentry_url)
