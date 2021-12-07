import pytest
from starlette import applications, testclient

from snowfall.junction.client_api import bootstrap, loaders, validation


@pytest.fixture()
def app() -> applications.Starlette:
    return bootstrap.create_app(
        validator=validation.Validator(
            "fixtures/test.json",
            loaders.PkgLoader("snowfall.junction.client_api"),
        ),
    )


@pytest.fixture()
def client(app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(app)


@pytest.fixture()
def error_client(app: applications.Starlette) -> testclient.TestClient:
    return testclient.TestClient(app, raise_server_exceptions=False)
