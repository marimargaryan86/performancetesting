from typing import Any

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.distribusion.httpx_logger import with_logging
from snowfall.vendor.duffel import client

TIMEOUT = 50.0
API_BASE_URL = "https://api.duffel.com"


@pytest.fixture()
def http_client() -> httpx.AsyncClient:
    return with_logging(httpx.AsyncClient(timeout=TIMEOUT))


@pytest.fixture()
def duffel_client(http_client: httpx.AsyncClient) -> client.DuffelClient:
    return client.DuffelClient(
        api_base_url=API_BASE_URL,
        api_key="duffel_test_mwCE9C8Ai452UaenWhexo9PQuz1VWbmzzU9ejcVDy3p",
        version="v1",
        http_client=http_client,
    )


def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.duffel.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    with open(file_path) as json_file:
        return json_util.loads(json_file.read())
