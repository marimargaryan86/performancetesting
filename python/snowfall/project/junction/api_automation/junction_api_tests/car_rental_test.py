import datetime
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import pytest
from httpx import HTTPStatusError

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@dataclass(frozen=True)
class InputSearchData:
    pickup_location: Mapping[str, Any]
    return_location: Mapping[str, Any]
    pickup_at: str
    return_at: str
    driver_age: int


BASIC_SEARCH = InputSearchData(
    pickup_location={"latitude": 50.89369066956447, "longitude": 4.47136870945399},
    return_location={"latitude": 48.96691462802318, "longitude": 2.52817297961273},
    pickup_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    return_at=(
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z"),
    driver_age=28,
)

NO_RESULTS_PICKUP_DATE = (  # No results for pickup after 2050
    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=365 * 50)
).strftime("%Y-%m-%dT08:00:00.000Z")
NO_RESULTS_RETURN_DATE = (  # No results for RETURN after 2050
    datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=(365 * 50) + 10)
).strftime("%Y-%m-%dT08:00:00.000Z")
COORDINATES = MappingProxyType({
    "ocean": {
        "latitude": -30.14512718,
        "longitude": 61.25976562,
    },
})


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_car_rental_search(
    qa_client: QaClient,
) -> None:
    car_rental_search = await qa_client.car_rental.search(
        pickup_location=BASIC_SEARCH.pickup_location,
        return_location=BASIC_SEARCH.return_location,
        pickup_at=BASIC_SEARCH.pickup_at,
        return_at=BASIC_SEARCH.return_at,
        driver_age=BASIC_SEARCH.driver_age,
    )
    assert car_rental_search.id

    car_rental_search = await qa_client.car_rental.wait_for_completed_search(
        search_id=car_rental_search.id,
    )
    assert car_rental_search.status == "completed"

    car_rental_offers = await qa_client.car_rental.get_offers(
        search_id=car_rental_search.id,
    )
    assert car_rental_offers.data
    assert car_rental_offers.offers


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("pickup_location", "return_location", "pickup_at", "return_at", "driver_age"),
    [
        (
            None,
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            {},
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            None,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            {},
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            None,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            None,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            None,
            BASIC_SEARCH.driver_age,
        ),
    ],
    ids=[
        "Search where Pickup Location is None, expecting HTTPStatusError, 400",
        "Search where Pickup Location is empty, expecting HTTPStatusError, 400",
        "Search where Return Location is None, expecting HTTPStatusError, 400",
        "Search where Return Location is empty, expecting HTTPStatusError, 400",
        "Search where Driver Age is None, expecting HTTPStatusError, 400",
        "Search where Pickup At is in None, expecting HTTPStatusError, 400",
        "Search where Return At is in None, expecting HTTPStatusError, 400",
    ],
)
async def test_car_rental_search_missing_or_none(
    qa_client: QaClient,
    pickup_location: Mapping[str, Any] | None,
    return_location: Mapping[str, Any] | None,
    pickup_at: str | None,
    return_at: str | None,
    driver_age: int | None,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.car_rental.search(
            pickup_location=pickup_location,
            return_location=return_location,
            pickup_at=pickup_at,
            return_at=return_at,
            driver_age=driver_age,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize(
    ("pickup_location", "return_location", "pickup_at", "return_at", "driver_age"),
    [
        (
            {"latitude": 200.89369066956447, "longitude": 4.47136870945399},
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            {"latitude": 48.96691462802318, "longitude": -200.52817297961273},
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            (
                datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=-1)
            ).strftime(
                "%Y-%m-%dT08:00:00.000Z",
            ),
            BASIC_SEARCH.return_at,
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            (
                datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=-1)
            ).strftime(
                "%Y-%m-%dT08:00:00.000Z",
            ),
            BASIC_SEARCH.driver_age,
        ),
        (
            BASIC_SEARCH.pickup_location,
            BASIC_SEARCH.return_location,
            BASIC_SEARCH.pickup_at,
            BASIC_SEARCH.return_at,
            0,
        ),
    ],
    ids=[
        "Search where Pickup Location is out of bounds, expecting HTTPStatusError, 400",
        "Search where Return Location is out of bounds, expecting HTTPStatusError, 400",
        "Search where Pickup At is in Past, expecting HTTPStatusError, 400",
        "Search where Return At is in Past, expecting HTTPStatusError, 400",
        "Search where Driver Age is 0, expecting HTTPStatusError, 400",
    ],
)
async def test_car_rental_search_invalid(
    qa_client: QaClient,
    pickup_location: Mapping[str, Any],
    return_location: Mapping[str, Any],
    pickup_at: str,
    return_at: str,
    driver_age: int,
) -> None:
    with pytest.raises(HTTPStatusError, match="Client error '400 Bad Request"):
        await qa_client.car_rental.search(
            pickup_location=pickup_location,
            return_location=return_location,
            pickup_at=pickup_at,
            return_at=return_at,
            driver_age=driver_age,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_car_rental_get_offers_result_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.car_rental.get_search_result(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_car_rental_get_offer_list_with_invalid_search_id(
    qa_client: QaClient,
) -> None:
    invalid_search_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

    with pytest.raises(HTTPStatusError, match="Client error '404 Not Found"):
        await qa_client.car_rental.get_offers(
            search_id=invalid_search_id,
        )


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_car_rental_search_for_no_offers(
    qa_client: QaClient,
) -> None:
    car_rental_search = await qa_client.car_rental.search(
        pickup_location=BASIC_SEARCH.pickup_location,
        return_location=BASIC_SEARCH.return_location,
        pickup_at=NO_RESULTS_PICKUP_DATE,
        return_at=NO_RESULTS_RETURN_DATE,
        driver_age=BASIC_SEARCH.driver_age,
    )
    assert car_rental_search.id

    car_rental_search = await qa_client.car_rental.wait_for_completed_search(
        search_id=car_rental_search.id,
    )
    assert car_rental_search.status == "completed"

    car_rental_offers = await qa_client.car_rental.get_offers(
        search_id=car_rental_search.id,
    )
    assert not car_rental_offers.data


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
async def test_mock_car_rental_search(
    qa_client: QaClient,
) -> None:
    car_rental_search = await qa_client.car_rental.search(
        pickup_location=COORDINATES["ocean"],
        return_location=COORDINATES["ocean"],
        pickup_at=BASIC_SEARCH.pickup_at,
        return_at=BASIC_SEARCH.return_at,
        driver_age=BASIC_SEARCH.driver_age,
    )
    assert car_rental_search.id

    car_rental_search = await qa_client.car_rental.wait_for_completed_search(
        search_id=car_rental_search.id,
    )
    assert car_rental_search.status == "completed"

    car_rental_offers = await qa_client.car_rental.get_offers(
        search_id=car_rental_search.id,
    )
    assert car_rental_offers.data
    assert car_rental_offers.offers
