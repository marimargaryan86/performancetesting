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
    origin: str
    destination: str
    depart_after: str
    passengers: Sequence[datetime.date]


BASIC_SEARCH = InputSearchData(
    origin="b917b2a4-b8d6-53d6-b9b9-a90eb1da01af",  # LAX
    destination="c7dcabc2-a4e1-5b78-8314-0891095205ae",  # JFK
    depart_after=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime(
        "%Y-%m-%dT08:00:00.000Z",
    ),
    passengers=[datetime.date(1980, 2, 3)],
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_flight_search_one_way(
    qa_client: QaClient,
) -> None:
    search_result = await qa_client.flight.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.depart_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )

    assert search_result.status == "pending"
    assert search_result.id

    search_result = await qa_client.flight.wait_for_completed_search(
        search_id=search_result.id,
    )
    assert search_result.status == "completed"

    search_offers = await qa_client.flight.get_offers(
        search_id=search_result.id,
    )
    assert search_offers.first_offer_id
    assert search_offers.first_result_offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.skip("Getting stuck with status Pending: ./bugs-triage/-/issues/166")
async def test_flight_search_with_no_offers(
    qa_client: QaClient,
) -> None:
    search_result = await qa_client.flight.search(
        origin="6da9e96b-5f05-5034-b5d5-993086525f0d",
        destination="6a797d54-6d61-5cab-afee-bcc97cbc9bc1",
        departure_after=BASIC_SEARCH.depart_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )

    assert search_result.status == "pending"
    assert search_result.id

    search_result = await qa_client.flight.wait_for_completed_search(
        search_id=search_result.id,
    )
    assert search_result.status == "completed"

    search_offers = await qa_client.flight.get_offers(
        search_id=search_result.id,
    )
    assert not search_offers.first_result_offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "passengers"),
    [
        (
            None,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            "",
            BASIC_SEARCH.destination,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            None,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            "",
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            BASIC_SEARCH.depart_after,
            [],
        ),
        (
            BASIC_SEARCH.origin,
            BASIC_SEARCH.destination,
            (
                datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=-1)
            ).strftime(
                "%Y-%m-%dT08:00:00.000Z",
            ),
            BASIC_SEARCH.passengers,
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
        "Search where depart is in past, expecting HTTPStatusError, 400",
        "Search where depart is in None, expecting HTTPStatusError, 400",
    ],
)
async def test_flight_search_missing_or_none(
    qa_client: QaClient,
    origin: str | None,
    destination: str | None,
    departure_after: str | None,
    passengers: Sequence[datetime.date],
) -> None:
    if departure_after and BASIC_SEARCH.depart_after != departure_after:
        pytest.skip("Skipping: waiting on fix for /bugs-triage/-/issues/153")

    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.flight.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_flight_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found' for url"):
        await qa_client.flight.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_flight_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found' for url"):
        await qa_client.flight.get_offers(
            search_id=invalid_search_id,
        )
