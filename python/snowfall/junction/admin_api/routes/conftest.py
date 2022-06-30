from typing import Any, Mapping, Optional, Sequence

import pytest
from starlette import applications, testclient
from starlette.middleware import Middleware

from snowfall.adapter import places
from snowfall.junction.admin_api import bootstrap, router
from snowfall.stdlib.integration.starlette import application
from snowfall.stdlib.persistence import filesystem


def _create_app(
    places_client: places.Client,
    openapi_specification: Mapping[str, Any],
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return application.create_starlette_app(
        routes_factory=router.get_routes,
        custom_middlewares=custom_middlewares,
        dependencies=bootstrap.create_dependencies(
            places_client=places_client,
        ),
        openapi_specification=openapi_specification,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "foobar",
    }


@pytest.fixture()
def app(
    places_client: places.Client,
) -> applications.Starlette:
    return _create_app(
        places_client=places_client,
        custom_middlewares=[],
        openapi_specification=filesystem.PkgLoader("admin_api").load("openapi.json"),
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
def unauthorized_client(
    client: testclient.TestClient,
) -> testclient.TestClient:
    client.headers.pop("Authorization")

    return client
