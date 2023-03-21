from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
from bson import json_util

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.benerail import client

API_BASE_URL = "https://test_url"


@pytest.fixture
async def httpx_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture
def benerail_client(httpx_client: httpx.AsyncClient) -> client.BenerailClient:
    return client.BenerailClient(
        subscription_key="xxxx",
        base_url=API_BASE_URL,
        http_client=httpx_client,
    )


def load_file_fixture(
    file_name: str,
) -> Any:
    file_path = filesystem.resource_path(
        package="snowfall.vendor.benerail.conftest",
        resource="fixtures/{file_name}".format(
            file_name=file_name,
        ),
    )

    with open(file_path) as json_file:
        return json_util.loads(json_file.read())
