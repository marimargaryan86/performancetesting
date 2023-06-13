import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from snowfall.project.junction.provider import notifications
from snowfall.project.junction.service.providers.karhoo import booking
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.karhoo import client


def load_json_fixture(
    file_name: str,
) -> dict[str, Any]:
    file_path = filesystem.resource_path(
        package="snowfall.project.junction.service.providers.karhoo.conftest",
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    with open(file_path) as file_handle:
        return json.load(file_handle)


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def karhoo_client(http_client: httpx.AsyncClient) -> client.KarhooClient:
    return client.KarhooClient(  # nosec
        api_key="key",
        base_url="https://test_url",
        http_client=http_client,
    )


@pytest.fixture()
def karhoo_booking_handler(
    karhoo_client: client.KarhooClient,
) -> booking.BookingHandler:
    return booking.BookingHandler(
        karhoo_client=karhoo_client,
        notifier=notifications.LogNotifier(),
    )
