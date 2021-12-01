import pytest
from starlette import testclient

from snowfall.junction.client_api import main


@pytest.fixture(scope="session")
def client() -> testclient.TestClient:
    return testclient.TestClient(main.app)
