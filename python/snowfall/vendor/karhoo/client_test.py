import uuid

import pytest
import pytest_httpx

from snowfall.stdlib.transport.http import errors
from snowfall.vendor.karhoo import client
from snowfall.vendor.karhoo.models import location


async def test_request_quotes(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes",
        status_code=201,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "availability": {},
            "quotes": [],
            "status": "PROGRESSING",
        },
    )

    quotes = await karhoo_client.request_quotes(
        origin=location.Coordinates(
            latitude=51.5054564,
            longitude=-0.0775452,
            display_address=None,
        ),
        destination=location.Coordinates(
            latitude=51.501364,
            longitude=-0.14189,
            display_address=None,
        ),
        departure_at=None,
    )

    assert quotes.id == uuid.UUID("00000000-0000-0000-0000-000000000000")


async def test_list_quotes(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes/00000000-0000-0000-0000-000000000000",
        status_code=200,
        json={
            "id": "00000000-0000-0000-0000-000000000000",
            "availability": {},
            "quotes": [],
            "status": "PROGRESSING",
        },
    )

    quotes = await karhoo_client.list_quotes(
        uuid.UUID("00000000-0000-0000-0000-000000000000"),
    )

    assert quotes.id == uuid.UUID("00000000-0000-0000-0000-000000000000")


async def test_list_quotes_not_found(
    httpx_mock: pytest_httpx.HTTPXMock,
    karhoo_client: client.KarhooClient,
) -> None:
    httpx_mock.add_response(
        url="https://test_url/v2/quotes/00000000-0000-0000-0000-000000000000",
        status_code=404,
        json={
            "code": "K3003",
            "message": "Could not get estimates, could not find specified quote,",
        },
    )

    with pytest.raises(errors.HttpStatusError) as exc:
        await karhoo_client.list_quotes(
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
        )

    assert (
        exc.value.body["message"]  # noqa: WPS441
        == "Could not get estimates, could not find specified quote,"
    )
