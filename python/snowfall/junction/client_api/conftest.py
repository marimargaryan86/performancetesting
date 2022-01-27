from typing import AsyncIterator

import pytest
from starlette import applications, testclient

from snowfall.adapter import places, trip_searches
from snowfall.junction.client_api import bootstrap, loaders, patch, validation


def _create_app(
    validator: validation.Validator,
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
) -> applications.Starlette:
    return bootstrap.create_app(
        validator=validator,
        dependencies=bootstrap.create_dependencies(
            places_client=places_client,
            trip_searches_client=trip_searches_client,
        ),
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer foobar",
    }


@pytest.fixture()
def app(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
) -> applications.Starlette:
    patch.patch_open_api()

    return _create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
        places_client=places_client,
        trip_searches_client=trip_searches_client,
    )


@pytest.fixture()
def client(
    app: applications.Starlette,
    headers: dict[str, str],
) -> testclient.TestClient:
    client = testclient.TestClient(app)
    client.headers.update(headers)

    return client


@pytest.fixture()
def test_app(
    places_client: places.Client,
    trip_searches_client: trip_searches.Client,
) -> applications.Starlette:
    patch.patch_open_api()

    return _create_app(
        validator=validation.Validator(
            "python/snowfall/junction/client_api/fixtures/test.json",
            loaders.FileLoader(),
        ),
        places_client=places_client,
        trip_searches_client=trip_searches_client,
    )


@pytest.fixture()
async def test_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture()
async def test_error_client(
    test_app: applications.Starlette,
) -> AsyncIterator[testclient.TestClient]:
    with testclient.TestClient(test_app) as client:
        yield client
