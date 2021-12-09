import uuid

import pytest
from starlette import applications, testclient

from snowfall.junction.client_api import bootstrap, loaders, places, validation

PLACE_NOT_FOUND = uuid.UUID("f55b0ec5-7c87-4c35-86f4-1417a5f50e89")
PLACES = (
    {"id": "f236a92c-4cfa-468e-85ef-431d25dcd925"},
    {"id": "488a836d-ec22-439b-a9d8-3c4c386a731e"},
)


@pytest.fixture()
def place_repository() -> places.PlaceRepository:
    return places.PlaceRepository(PLACES)


def _create_app(
    validator: validation.Validator,
    place_repository: places.PlaceRepository,
) -> applications.Starlette:
    return bootstrap.create_app(
        validator=validator,
        dependencies=bootstrap.create_dependencies(
            place_repository=place_repository,
        ),
    )


@pytest.fixture()
def app(place_repository: places.PlaceRepository) -> applications.Starlette:
    return _create_app(
        validator=validation.Validator(
            "openapi.json",
            loaders.PkgLoader("client_api"),
        ),
        place_repository=place_repository,
    )


@pytest.fixture()
def client(app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(app)


@pytest.fixture()
def test_app(place_repository: places.PlaceRepository) -> applications.Starlette:
    return _create_app(
        validator=validation.Validator(
            "fixtures/test.json",
            loaders.PkgLoader("snowfall.junction.client_api"),
        ),
        place_repository=place_repository,
    )


@pytest.fixture()
def test_client(test_app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(test_app)


@pytest.fixture()
def test_error_client(test_app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(test_app, raise_server_exceptions=False)
