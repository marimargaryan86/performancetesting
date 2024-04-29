import datetime
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)

pytestmark = pytest.mark.skip(
    reason="Skipping tests - Ferry not working and/or priority",
)


@dataclass(frozen=True)
class InputSearchData:
    origin: Mapping[str, Any]
    destination: Mapping[str, Any]
    departure_after: str
    return_at: str
    passengers: Sequence[datetime.date]


BASIC_SEARCH = InputSearchData(
    origin={"latitude": 51.94743, "longitude": 1.2533101},
    destination={"latitude": 51.9754793, "longitude": 4.1255803},
    departure_after=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    return_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    passengers=[datetime.date(1980, 2, 3)],
)

INVALID_SEARCH = InputSearchData(
    origin={"latitude": 240.7127753, "longitude": 1.2533101},
    destination={"latitude": 251.9754793, "longitude": 4.1255803},
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
async def test_ferry_search(
    qa_client: QaClient,
) -> None:
    ferry_search = await qa_client.ferry.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.departure_after,
        return_at=BASIC_SEARCH.return_at,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )
    assert ferry_search.id

    ferry_search = await qa_client.ferry.wait_for_completed_search(
        search_id=ferry_search.id,
    )
    assert ferry_search.status == "completed"

    ferry_offers = await qa_client.ferry.get_offers(
        search_id=ferry_search.id,
    )
    assert ferry_offers.offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "return_at", "passengers"),
    [
        (
            None,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            {},
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            None,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            {},
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            [],
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            None,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
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
        "Search where Return At in None, expecting HTTPStatusError, 400",
    ],
)
async def test_ferry_search_missing_or_none(
    qa_client: QaClient,
    origin: Mapping[str, Any] | None,
    destination: Mapping[str, Any] | None,
    departure_after: str | None,
    return_at: str | None,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.ferry.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            return_at=return_at,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "return_at", "passengers"),
    [
        (
            INVALID_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            INVALID_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            INVALID_SEARCH.departure_after,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            INVALID_SEARCH.return_at,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.departure_after,
            INVALID_SEARCH.return_at,
            INVALID_SEARCH.passengers,
        ),
    ],
    ids=[
        "Search where Origin is Invalid, expecting HTTPStatusError, 400",
        "Search where Destination is Invalid, expecting HTTPStatusError, 400",
        "Search where Departure After is in past, expecting HTTPStatusError, 400",
        "Search where Return At in past, expecting HTTPStatusError, 400",
        "Search where passengers is Invalid, expecting HTTPStatusError, 400",
    ],
)
async def test_ferry_search_invalid(
    qa_client: QaClient,
    origin: Mapping[str, Any] | None,
    destination: Mapping[str, Any] | None,
    departure_after: str,
    return_at: str,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(
        HTTPStatusError,
        match="Client error '400 Bad Request",
    ):
        await qa_client.ferry.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            return_at=return_at,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_ferry_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.ferry.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_ferry_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.ferry.get_offers(
            search_id=invalid_search_id,
        )
