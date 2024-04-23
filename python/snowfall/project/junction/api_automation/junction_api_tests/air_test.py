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
    origin_iata: str
    destination_iata: str
    depart_after: str
    passengers: Sequence[datetime.date]


BASIC_SEARCH = InputSearchData(
    origin_iata="LAX",
    destination_iata="JFK",
    depart_after=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime(
        "%Y-%m-%dT08:00:00.000Z",
    ),
    passengers=[datetime.date(1980, 2, 3)],
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_air_search_with_iata(
    qa_client: QaClient,
) -> None:
    search_result = await qa_client.air.search(
        origin=BASIC_SEARCH.origin_iata,
        destination=BASIC_SEARCH.destination_iata,
        departure_after=BASIC_SEARCH.depart_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )

    assert search_result.status == "pending"
    assert search_result.id

    search_result = await qa_client.air.wait_for_completed_search(
        search_id=search_result.id,
    )
    assert search_result.status == "completed"

    search_offers = await qa_client.air.get_offers(
        search_id=search_result.id,
    )
    assert search_offers.offers
    assert search_offers.first_offer_id


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_air_search_with_no_offers(
    qa_client: QaClient,
) -> None:
    search_result = await qa_client.air.search(
        origin="LON",
        destination="PAR",
        departure_after=BASIC_SEARCH.depart_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )

    assert search_result.status == "pending"
    assert search_result.id

    search_result = await qa_client.air.wait_for_completed_search(
        search_id=search_result.id,
    )
    assert search_result.status == "completed"

    search_offers = await qa_client.air.get_offers(
        search_id=search_result.id,
    )
    assert not search_offers.offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("origin", "destination", "departure_after", "passengers"),
    [
        (
            None,
            BASIC_SEARCH.destination_iata,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            "",
            BASIC_SEARCH.destination_iata,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin_iata,
            None,
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin_iata,
            "",
            BASIC_SEARCH.depart_after,
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin_iata,
            BASIC_SEARCH.destination_iata,
            BASIC_SEARCH.depart_after,
            [],
        ),
        (
            BASIC_SEARCH.origin_iata,
            BASIC_SEARCH.destination_iata,
            (
                datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=-1)
            ).strftime(
                "%Y-%m-%dT08:00:00.000Z",
            ),
            BASIC_SEARCH.passengers,
        ),
        (
            BASIC_SEARCH.origin_iata,
            BASIC_SEARCH.destination_iata,
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
async def test_air_search_missing_or_none(
    qa_client: QaClient,
    origin: str | None,
    destination: str | None,
    departure_after: str | None,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.air.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_air_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found' for url"):
        await qa_client.air.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_air_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found' for url"):
        await qa_client.air.get_offers(
            search_id=invalid_search_id,
        )
