import datetime
from collections.abc import Sequence
from dataclasses import dataclass

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@dataclass(frozen=True)
class InputSearchData:
    latitude: float
    longitude: float
    checkin_at: str
    checkout_at: str
    radius: int
    passengers: Sequence[datetime.date]


BASIC_SEARCH = InputSearchData(
    latitude=40.7127753,
    longitude=-74.0059728,
    checkin_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    checkout_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    radius=20,
    passengers=[datetime.date(1980, 2, 3)],
)

INVALID_SEARCH = InputSearchData(
    latitude=240.7127753,
    longitude=-274.0059728,
    checkin_at=(
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    checkout_at=(
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    radius=-10,
    passengers=[datetime.date(2050, 2, 3)],
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_hotel_search(
    qa_client: QaClient,
) -> None:
    hotel_search = await qa_client.hotel.search(
        latitude=BASIC_SEARCH.latitude,
        longitude=BASIC_SEARCH.longitude,
        checkin_at=BASIC_SEARCH.checkin_at,
        checkout_at=BASIC_SEARCH.checkout_at,
        radius=BASIC_SEARCH.radius,
        passengers=BASIC_SEARCH.passengers,
    )
    assert hotel_search.id

    hotel_search = await qa_client.hotel.wait_for_completed_search(
        search_id=hotel_search.id,
    )
    assert hotel_search.status == "completed"

    hotel_search_offers = await qa_client.hotel.get_offers(
        search_id=hotel_search.id,
    )
    assert hotel_search_offers.offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("latitude", "longitude", "checkin_at", "checkout_at", "radius", "passengers"),
    [
        (
            None,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            "",
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            None,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            "",
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            None,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            None,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            None,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            [],
        ),
    ],
    ids=[
        "Search where Latitude is None, expecting HTTPStatusError, 400",
        "Search where Latitude is empty, expecting HTTPStatusError, 400",
        "Search where Longitude is None, expecting HTTPStatusError, 400",
        "Search where Longitude is empty, expecting HTTPStatusError, 400",
        "Search where Checkin At is None, expecting HTTPStatusError, 400",
        "Search where Checkout At is None, expecting HTTPStatusError, 400",
        "Search where Radius is None, expecting HTTPStatusError, 400",
        "Search where passengers are empty, expecting HTTPStatusError, 400",
    ],
)
async def test_hotel_search_missing_or_none(
    qa_client: QaClient,
    latitude: float | None,
    longitude: float | None,
    checkin_at: str | None,
    checkout_at: str | None,
    radius: int | None,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.hotel.search(
            latitude=latitude,
            longitude=longitude,
            checkin_at=checkin_at,
            checkout_at=checkout_at,
            radius=radius,
            passengers=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("latitude", "longitude", "checkin_at", "checkout_at", "radius", "passengers"),
    [
        (
            INVALID_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            INVALID_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            INVALID_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            INVALID_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            INVALID_SEARCH.radius,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.latitude,
            BASIC_SEARCH.longitude,
            BASIC_SEARCH.checkin_at,
            BASIC_SEARCH.checkout_at,
            BASIC_SEARCH.radius,
            INVALID_SEARCH.passengers,
        ),
    ],
    ids=[
        "Search where Latitude is Invalid, expecting HTTPStatusError, 400",
        "Search where Longitude is Invalid, expecting HTTPStatusError, 400",
        "Search where Checkin At is in past, expecting HTTPStatusError, 400",
        "Search where Checkout At in past, expecting HTTPStatusError, 400",
        "Search where Radius is negative, expecting HTTPStatusError, 400",
        "Search where passengers is Invalid, expecting HTTPStatusError, 400",
    ],
)
async def test_hotel_search_invalid(
    qa_client: QaClient,
    latitude: float,
    longitude: float,
    checkin_at: str,
    checkout_at: str,
    radius: int,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.hotel.search(
            latitude=latitude,
            longitude=longitude,
            checkin_at=checkin_at,
            checkout_at=checkout_at,
            radius=radius,
            passengers=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_hotel_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.hotel.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_hotel_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.hotel.get_offers(
            search_id=invalid_search_id,
        )
