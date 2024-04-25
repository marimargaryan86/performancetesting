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
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=2)
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
async def test_train_search_one_way(
    qa_client: QaClient,
) -> None:
    trian_search = await qa_client.train.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.departure_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
    )
    assert trian_search.id

    train_search_result = await qa_client.train.wait_for_completed_search(
        search_id=trian_search.id,
    )
    assert train_search_result.status == "completed"

    train_offers = await qa_client.train.get_offers(
        search_id=train_search_result.id,
    )
    assert train_offers.offer_results
    assert train_offers.offer_results[0].offer_ids
    assert train_offers.offer_results[0].result_detail_ids


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_train_search_return(  # noqa: WPS217,WPS218
    qa_client: QaClient,
) -> None:
    outbound_search = await qa_client.train.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.departure_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
        return_at=BASIC_SEARCH.return_at,
    )

    train_search_result = await qa_client.train.wait_for_completed_search(
        search_id=outbound_search.id,
    )

    train_offers = await qa_client.train.get_offers(
        search_id=train_search_result.id,
    )

    assert train_offers.offer_results
    first_result_first_offer = train_offers.offer_results[0].offer_ids[0]

    return_search = await qa_client.train.search(
        origin=BASIC_SEARCH.origin,
        destination=BASIC_SEARCH.destination,
        departure_after=BASIC_SEARCH.departure_after,
        passengers_dates_of_birth=BASIC_SEARCH.passengers,
        return_at=BASIC_SEARCH.return_at,
        outbound_offer_id=first_result_first_offer,
    )

    return_search_result = await qa_client.train.wait_for_completed_search(
        search_id=return_search.id,
    )

    return_offers = await qa_client.train.get_offers(
        search_id=return_search_result.id,
    )

    assert return_offers.offer_results
    assert return_offers.offer_results[0].offer_ids
    assert return_offers.offer_results[0].result_detail_ids


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
async def test_train_search_missing_or_none(
    qa_client: QaClient,
    origin: str | None,
    destination: str | None,
    departure_after: str | None,
    passengers: Sequence[datetime.date],
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.train.search(
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
async def test_train_search_invalid(
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
        await qa_client.train.search(
            origin=origin,
            destination=destination,
            departure_after=departure_after,
            passengers_dates_of_birth=passengers,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_train_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.train.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_train_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.train.get_offers(
            search_id=invalid_search_id,
        )
