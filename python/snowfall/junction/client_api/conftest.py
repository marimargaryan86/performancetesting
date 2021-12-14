from typing import AsyncIterator

import pytest
from starlette import applications, testclient

from snowfall.junction.client_api import (
    bootstrap,
    journeys,
    loaders,
    patch,
    places,
    validation,
)

PLACE_NOT_FOUND = "f55b0ec5-7c87-4c35-86f4-1417a5f50e89"
PLACES = (
    {"id": "f236a92c-4cfa-468e-85ef-431d25dcd925"},
    {"id": "488a836d-ec22-439b-a9d8-3c4c386a731e"},
)


@pytest.fixture()
def place_repository() -> places.PlaceRepository:
    return places.PlaceRepository(PLACES)


@pytest.fixture()
def journey_search_repository() -> journeys.JourneySearchRepository:
    return journeys.JourneySearchRepository()


def _create_app(
    validator: validation.Validator,
    place_repository: places.PlaceRepository,
    journey_search_repository: journeys.JourneySearchRepository,
) -> applications.Starlette:
    return bootstrap.create_app(
        validator=validator,
        dependencies=bootstrap.create_dependencies(
            place_repository=place_repository,
            journey_search_repository=journey_search_repository,
        ),
    )


@pytest.fixture()
def app(
    place_repository: places.PlaceRepository,
    journey_search_repository: journeys.JourneySearchRepository,
) -> applications.Starlette:
    patch.patch_open_api()

    return _create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
        place_repository=place_repository,
        journey_search_repository=journey_search_repository,
    )


@pytest.fixture()
def client(app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(app)


@pytest.fixture()
def test_app(
    place_repository: places.PlaceRepository,
    journey_search_repository: journeys.JourneySearchRepository,
) -> applications.Starlette:
    patch.patch_open_api()

    return _create_app(
        validator=validation.Validator(
            "python/snowfall/junction/client_api/fixtures/test.json",
            loaders.FileLoader(),
        ),
        place_repository=place_repository,
        journey_search_repository=journey_search_repository,
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
