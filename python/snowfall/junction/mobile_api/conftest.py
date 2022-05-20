import http
from typing import Mapping, Optional, Sequence

import pytest
from lagom.integrations import starlette
from starlette import applications, testclient
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem


def _create_app(
    dependencies: starlette.StarletteIntegration,
    custom_middlewares: Optional[Sequence[Middleware]] = None,
) -> applications.Starlette:
    return bootstrap.create_app(
        dependencies=dependencies,
        custom_middlewares=custom_middlewares,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
    }


@pytest.fixture()
def app() -> applications.Starlette:
    return _create_app(
        bootstrap.create_dependencies(),
        [
            Middleware(
                middlewares.ValidationMiddleware,
                validator=validation.Validator(
                    "openapi.json",
                    filesystem.PkgLoader("mobile_api"),
                ),
                excluded_status_codes={http.HTTPStatus.METHOD_NOT_ALLOWED},
            ),
        ],
    )


@pytest.fixture()
def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    client = testclient.TestClient(app)
    client.headers.update(headers)

    return client
