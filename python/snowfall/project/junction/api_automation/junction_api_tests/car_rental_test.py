import datetime

import pytest

from snowfall.project.junction.api_automation.service_objects.qa_client import (
    QaClient,
)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.skip("Empty result for car rental search with mock")
async def test_car_rental_search(
    qa_client: QaClient,
) -> None:
    pickup_location = {"latitude": 50.89369066956447, "longitude": 4.47136870945399}
    return_location = {"latitude": 48.96691462802318, "longitude": 2.52817297961273}
    pickup_at = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=10)
    ).strftime("%Y-%m-%dT08:00:00.000Z")
    return_at = (
        datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=11)
    ).strftime("%Y-%m-%dT08:00:00.000Z")
    car_rental_search = await qa_client.car_rental.search(
        pickup_location=pickup_location,
        return_location=return_location,
        pickup_at=pickup_at,
        return_at=return_at,
        driver_age=28,
    )
    assert car_rental_search.id

    car_rental_search = await qa_client.car_rental.wait_for_completed_search(
        search_id=car_rental_search.id,
    )
    assert car_rental_search.status == "completed"

    car_rental_offers = await qa_client.car_rental.get_offers(
        search_id=car_rental_search.id,
    )
    assert car_rental_offers.id
