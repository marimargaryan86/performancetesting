import pathlib
from typing import Mapping, Optional, Sequence

import currencycloud
import pytest
from lagom.integrations import starlette
from starlette import applications, testclient
from starlette.middleware import Middleware

from snowfall.junction.pay_api import bootstrap
from snowfall.junction.pay_api.routes import router
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem


def _create_app(
    dependencies: starlette.StarletteIntegration,
    openapi_path: pathlib.Path,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        dependencies=dependencies,
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes_factory=router.get_routes,
    )


@pytest.fixture()
def cc_login() -> str:
    return "cc_login"


@pytest.fixture()
def cc_api_key() -> str:
    return "random_key"


@pytest.fixture()
def cc_env() -> str:
    return "demo"


@pytest.fixture()
def cc_client(cc_login: str, cc_api_key: str, cc_env: str) -> currencycloud.Client:
    return currencycloud.Client(
        cc_login,
        cc_api_key,
        cc_env,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
    }


@pytest.fixture()
def app(cc_client: currencycloud.Client) -> applications.Starlette:
    return _create_app(
        dependencies=bootstrap.create_dependencies(cc_client),
        openapi_path=filesystem.resource_path("pay_api", "openapi.json"),
    )


@pytest.fixture()
def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    client = testclient.TestClient(app)
    client.headers.update(headers)

    return client


@pytest.fixture()
def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    http_client = testclient.TestClient(app)
    http_client.headers.update(headers)

    return http_client
