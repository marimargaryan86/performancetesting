from collections.abc import AsyncIterator
from typing import Any

import aiofiles
import httpx
import orjson
import pytest

from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.providers.karhoo import booking
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.karhoo import client


async def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.karhoo.conftest",
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
def karhoo_client(http_client: httpx.AsyncClient) -> client.KarhooClient:
    return client.KarhooClient(
        api_key="key",
        base_url="https://test_url",
        http_client=http_client,
    )


@pytest.fixture()
async def storage() -> AsyncIterator[filesystem.Storage]:
    async with filesystem.Storage.from_dsn("memory://") as storage_obj:
        yield storage_obj


@pytest.fixture()
def karhoo_booking_handler(
    karhoo_client: client.KarhooClient,
    storage: filesystem.Storage,
) -> booking.BookingHandler:
    return booking.BookingHandler(
        karhoo_client=karhoo_client,
        notifier=notifications.LogNotifier(),
        booking_storage=storage,
    )
