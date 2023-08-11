import datetime
import json
import logging
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

import httpx
import hvac
import pytest

from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.project.junction.api_automation.test_functions.pay_webhook_client import (
    PayWebhookClient,
)
from snowfall.stdlib.transport.http import auth
from snowfall.vendor.junction.auth import UserAuth
from snowfall.vendor.junction.go.client import Client as GoClient
from snowfall.vendor.junction.pay.client import Client as PayClient

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
def add_allure_environment_property(  # noqa: WPS210
    request: pytest.FixtureRequest,
) -> Iterator[Callable[[str, Any], None]]:
    environment_properties = {}

    def maker(key: str, key_value: Any) -> None:  # noqa: WPS430
        environment_properties.update({key: key_value})

    yield maker

    allure_dir = request.config.getoption(ALLUREDIR_OPTION)
    if not allure_dir or not allure_dir.is_dir():
        return

    if not environment_properties:
        return

    allure_env_file = allure_dir / ALLURE_ENVIRONMENT_PROPERTIES_FILE
    file_data = "\n".join(
        [
            "{0}={1}".format(env_variable, env_value)
            for env_variable, env_value in environment_properties.items()
        ],
    )
    allure_env_file.write_text(file_data)


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


@pytest.fixture()
def pay_client(
    api_token: str,
    host: str,
) -> PayClient:
    email = get_variable_value(host, api_token, "pay_api_test_email")
    password = get_variable_value(host, api_token, "pay_api_test_password")
    base_url_admin_api = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_admin_api_host"),
    )
    base_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_api_host"),
    )

    auth = UserAuth(
        base_url=base_url_admin_api,
        email=email,
        password=password,
    )

    return PayClient(
        base_url=base_url,
        auth=auth,
    )


@pytest.fixture()
def pay_admin_client(
    api_token: str,
    host: str,
) -> PayAdminClient:
    email = get_variable_value(host, api_token, "pay_api_test_email")
    password = get_variable_value(host, api_token, "pay_api_test_password")

    base_url_admin_api = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_admin_api_host"),
    )

    auth = UserAuth(
        base_url=base_url_admin_api,
        email=email,
        password=password,
    )

    return PayAdminClient(
        base_url=base_url_admin_api,
        auth=auth,
    )


@pytest.fixture()
def pay_webhook_client(
    api_token: str,
    host: str,
) -> PayWebhookClient:
    base_url_webhook_api = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_webhook_host"),
    )
    return PayWebhookClient(
        base_url=base_url_webhook_api,
    )


@pytest.fixture()
async def pay_create_beneficiary(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="EUR test Account Holder",
            email="example@example.com",
            beneficiary_address_lines=[
                "Radhuset",
                "Våksalagatan 2",
                "United Spaces",
                "Sweden",
            ],
            beneficiary_country_code="DE",
            bank_name="mBank S.A.",
            account_type="checking",
            payment_types="priority",
            bank_address_lines=[
                "mBank S.A.",
                "Bankowość detaliczna",
                "Skrytka Pocztowa 2108",
                "90-959",
                "Łódź 2",
            ],
            bank_country_code="DE",
            currency_id="EUR",
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban="DE89370400440532013000",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )
    return response_create_beneficiary


PAY_TEST_ACCOUNT01 = "7e249624-535d-418a-8009-0908675136e1"
PAY_TEST_ACCOUNT02 = "026b616f-8e6b-42e4-abc7-559ef58a4d69"
