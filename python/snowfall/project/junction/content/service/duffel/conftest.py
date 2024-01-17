from collections.abc import AsyncIterator
from typing import Any

import aiofiles
import httpx
import orjson
import pytest

from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.duffel import client


async def load_json_fixture(
    file_name: str,
    package: str | None = None,
) -> dict[str, Any]:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def duffel_client(http_client: httpx.AsyncClient) -> client.DuffelClient:
    return client.DuffelClient(
        api_base_url="http://localhost",
        api_key="foo",
        version="bar",
        http_client=http_client,
    )
