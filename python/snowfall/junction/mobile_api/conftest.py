import datetime
import http
from typing import Mapping, Optional, Sequence

import pytest
from lagom.integrations import starlette
from starlette import applications, testclient
from starlette.middleware import Middleware

from snowfall.junction.mobile_api import bootstrap, repository
from snowfall.stdlib.integration.starlette import middlewares, validation
from snowfall.stdlib.persistence import filesystem, redis
from snowfall.vendor.junction import client


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
def api_url() -> str:
    return "http://localhost:8000"


@pytest.fixture()
def token() -> str:
    return "random_token"


@pytest.fixture()
def junction_client(
    api_url: str,
    token: str,
) -> client.JunctionClient:
    return client.JunctionClient(
        api_url=api_url,
        token=token,
    )


@pytest.fixture()
def places_repository(
    junction_client: client.JunctionClient,
    redis_client: redis.Client[str],
) -> repository.PlacesRepository:
    return repository.PlacesRepository(
        junction_client=junction_client,
        redis_client=redis_client,
        cache_ttl=datetime.timedelta(seconds=10),
    )


@pytest.fixture()
def app(
    places_repository: repository.PlacesRepository,
) -> applications.Starlette:
    return _create_app(
        bootstrap.create_dependencies(places_repository),
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
def http_client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> testclient.TestClient:
    http_client = testclient.TestClient(app)
    http_client.headers.update(headers)

    return http_client
