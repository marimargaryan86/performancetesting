import base64
import datetime
import json
import logging
import tempfile
import urllib
from collections.abc import (
    AsyncGenerator,
    Callable,
    Iterator,
    Mapping,
    Sequence,
)
from itertools import starmap
from pathlib import Path
from typing import Any

import boto3
import httpx
import hvac
import pytest
from pymongo import MongoClient

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
def departures_after(request: pytest.FixtureRequest) -> Sequence[str]:
    departures = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT08:00:00.000Z")
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
    test_markers = [
        ("integration", "use `-m integration` to run this test"),
        ("smoke", "use `-m smoke` to run this test"),
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


def connect_to_aws() -> Any:
    aws_access_key_id = "AKIA6JO5TGEWJNIU4LNR"
    aws_secret_access_key = "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"
    bucket_name = "junctionqa"
    file_key = "rails_origin_destination.csv"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return response["Body"].read()


class ConfigurationManager(object):
    def __init__(self, host: str, api_token: str) -> None:
        self.host = host
        self.api_token = api_token

    def get_br_cert(self) -> str:
        br_base64_cert = get_variable_value(self.host, self.api_token, "br_base64_cert")
        return str(br_base64_cert)

    def get_br_api_host(self) -> str:
        br_api_host = get_variable_value(self.host, self.api_token, "br_api_host")
        return str(br_api_host)

    def get_br_subscription_key(self) -> str:
        br_subscription_key = get_variable_value(
            self.host,
            self.api_token,
            "br_subscription_key",
        )
        return str(br_subscription_key)


async def create_br_connection(
    config_manager: ConfigurationManager,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    cert = (config_manager.get_br_cert(),)
    base64_cert = "-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----".format(
        cert[0],
    )
    decoded_cert = base64.b64decode(urllib.parse.unquote(base64_cert))

    with tempfile.NamedTemporaryFile(delete=False) as temp_cert_file:
        temp_cert_file.write(decoded_cert)
        temp_cert_file_name = temp_cert_file.name
    async with httpx.AsyncClient(http2=True, cert=temp_cert_file_name) as client:
        yield client


async def make_br_request(
    config_manager: ConfigurationManager,
    method: str,
    endpoint: str,
    payload: Mapping[str, Any],
    custom_headers: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], Any]:
    base_url = config_manager.get_br_api_host()
    subscription_key = config_manager.get_br_subscription_key()
    full_url = urllib.parse.urljoin(base_url, endpoint)

    default_headers = {
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/json",
        "x-bnds-user-token": "ea44f55b-f390-4327-b3a7-9d79668d4f11",
    }
    headers = default_headers
    if custom_headers is not None:
        headers = {**default_headers, **custom_headers}
    async for conn in create_br_connection(config_manager):
        response = await conn.request(
            method,
            full_url,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        response_hearder = response.headers
        response_data = response.json()

        return response_data, response_hearder
    raise RuntimeError("Error on Benerail requests")


@pytest.fixture()
def config_manager(host: str, api_token: str) -> ConfigurationManager:
    return ConfigurationManager(host, api_token)
