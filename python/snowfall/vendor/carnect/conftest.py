from typing import Any

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.carnect import client, config

TIMEOUT = 50
API_BASE_URL = "https://ota2007a.micronnexus-staging.com/service.asmx"


@pytest.fixture
def carnect_config() -> config.Config:
    return config.Config(timeout=TIMEOUT, base_url=API_BASE_URL)


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT)


@pytest.fixture
def carnect_client(
    http_client: httpx.AsyncClient,
    carnect_config: config.Config,
) -> client.CarnectClient:
    return client.CarnectClient(http_client=http_client, config=carnect_config)


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
