import datetime
from collections.abc import Sequence
from dataclasses import dataclass

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import QaClient


@dataclass(frozen=True)
class InputSearchData:
    origin: str
    destination: str
    departure_after: str
    return_at: str
    passengers: Sequence[datetime.date]


BASIC_SEARCH = InputSearchData(
    origin="000ab964-4bd2-51d2-bb2b-85c94fb98bf9",
    destination="00568d06-4509-54d4-832e-68f1463128d8",
    departure_after=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    return_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    passengers=[datetime.date(1980, 2, 3)],
)

INVALID_SEARCH = InputSearchData(
    origin="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    destination="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    departure_after=(
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    return_at=(
        datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    passengers=[datetime.date(2050, 2, 3)],
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_rail_search(
    qa_client: QaClient,
) -> None:
    rail_search = await qa_client.rail.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.departure_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )
    assert rail_search.id

    rail_search_result = await qa_client.rail.wait_for_completed_search(
        search_id=rail_search.id,
    )
    assert rail_search_result.status == "completed"

    rail_offers = await qa_client.rail.get_offers(
        search_id=rail_search_result.id,
    )
    assert rail_offers.offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "passengers"),
    [
        (
            None,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            {},
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            None,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            {},
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            [],
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            None,
            BASIC_SEARCH.passengers,
        ),
    ],
    ids=[
        "Search where Origin is None, expecting HTTPStatusError, 400",
        "Search where Origin is empty, expecting HTTPStatusError, 400",
        "Search where Destination is None, expecting HTTPStatusError, 400",
        "Search where Destination is empty, expecting HTTPStatusError, 400",
        "Search where Passengers is empty list, expecting HTTPStatusError, 400",
        "Search where depart is in None, expecting HTTPStatusError, 400",
    ],
)
async def test_rail_search_missing_or_none(
    qa_client: QaClient,
    origin: str | None,
    destination: str | None,
    departure_after: str | None,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.rail.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "passengers"),
    [
        (
            INVALID_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            INVALID_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            INVALID_SEARCH.departure_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            INVALID_SEARCH.passengers,
        ),
    ],
    ids=[
        "Search where Origin is Invalid, expecting HTTPStatusError, 422",
        "Search where Destination is Invalid, expecting HTTPStatusError, 422",
        "Search where Departure After is in past, expecting HTTPStatusError, 422",
        "Search where passengers is Invalid, expecting HTTPStatusError, 422",
    ],
)
async def test_rail_search_invalid(
    qa_client: QaClient,
    origin: str | None,
    destination: str | None,
    departure_after: str,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(
        HTTPStatusError,
        match="Client error '422 Unprocessable Entity",
    ):
        await qa_client.rail.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_rail_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.rail.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_rail_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.rail.get_offers(
            search_id=invalid_search_id,
        )
