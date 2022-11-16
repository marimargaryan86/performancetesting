from typing import Any

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.distribusion import client

TIMEOUT = 50.0

API_BASE_URL = "https://api.demo.distribusion.com"


@pytest.fixture
def distribusion_client() -> client.DistribusionClient:
    return client.DistribusionClient(
        api_base_url=API_BASE_URL,
        api_key="MkQQ6J6BO2ooqwZYpM6fUmDu6rGwWXP1obaQuITo",
        retailer_partner_number="431926",
        http_client=httpx.AsyncClient(timeout=TIMEOUT),
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
