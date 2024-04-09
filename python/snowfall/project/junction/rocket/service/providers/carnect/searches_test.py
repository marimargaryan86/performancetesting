import datetime
import math

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.providers.carnect import (
    constants,
    criteria,
    searches,
)
from snowfall.stdlib import string
from snowfall.stdlib.v1 import latlng_pb2


async def test_successful(  # noqa: WPS218
    search_result_generator: searches.SearchResultGenerator,
) -> None:
    search_task = criteria.Criteria(
        search_id=string.uuid(),
        origin=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=50.89369066956447,
                longitude=4.47136870945399,
            ),
        ),
        destination=common_pb2.Point(
            coordinates=latlng_pb2.LatLng(
                latitude=48.96691462802318,
                longitude=2.52817297961273,
            ),
        ),
        pickup_datetime=datetime.datetime.now(tz=datetime.UTC),
        return_datetime=datetime.datetime.now(tz=datetime.UTC),
        driver_age=50,
    )
    results = [
        result
        async for result in search_result_generator.gather_search_results(search_task)
    ]

    assert len(results) == 114

    result = results[0]
    assert len(result.offers) == 1
    assert len(result.result_details) == 1
    assert result.provider_id == str(constants.PROVIDER_ID)

    result_detail = result.result_details[0]
    assert math.isclose(result_detail.car_rental.origin.coordinates.latitude, 50.846541)
    assert math.isclose(result_detail.car_rental.origin.coordinates.longitude, 4.351684)
    assert math.isclose(
        result_detail.car_rental.destination.coordinates.latitude,
        49.003526,
    )
    assert math.isclose(
        result_detail.car_rental.destination.coordinates.longitude,
        2.569589,
    )

    offer = result.offers[0]
    assert offer.price.units == 68
    assert offer.price.currency_code == "EUR"

    assert (
        result_detail.car_rental.image_url
        == "https://vehicles.carhire-solutions.com/371/small/48252_MBMR.jpg"
    )
    assert result_detail.car_rental.model == "A HYUNDAI I10"
    assert result_detail.car_rental.seats_count == 4
    assert result_detail.car_rental.doors_count == 2
    assert result_detail.car_rental.transmission == "Manual"
    assert result_detail.car_rental.baggage_quantity == 1
    assert result_detail.car_rental.vehicle_type == "Car"
    assert result_detail.car_rental.vendor_name == "Hertz"
    assert result_detail.car_rental.vendor_code == "ZE"
    assert result_detail.car_rental.unlimited_mileage
    assert result_detail.car_rental.air_conditioner
