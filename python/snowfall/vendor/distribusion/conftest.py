from typing import Any

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.httpx_logger import with_logging

TIMEOUT = 50.0
API_BASE_URL = "https://api.demo.distribusion.com"


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return with_logging(httpx.AsyncClient(timeout=TIMEOUT))


@pytest.fixture
def distribusion_client(http_client: httpx.AsyncClient) -> client.DistribusionClient:
    return client.DistribusionClient(
        api_base_url=API_BASE_URL,
        api_key="MkQQ6J6BO2ooqwZYpM6fUmDu6rGwWXP1obaQuITo",
        retailer_partner_number="431926",
        http_client=http_client,
    )


def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.distribusion.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    with open(file_path) as json_file:
        return json_util.loads(json_file.read())
