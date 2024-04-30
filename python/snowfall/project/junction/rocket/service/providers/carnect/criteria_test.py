from snowfall.project.junction.rocket.service.providers.carnect import criteria
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2,
)
from snowfall.stdlib.format import protobuf


async def test_search_criteria_generator_is_correct(
    search_criteria: models_pb2.Search,
) -> None:
    result = await criteria.search_criteria_generator(search_criteria)

    assert result == [
        criteria.Criteria(
            search_id="6bceb792-b6d6-4aec-a5ed-e825867385cf",
            origin=search_criteria.car_rental.origin,
            destination=search_criteria.car_rental.destination,
            pickup_datetime=protobuf.protobuf_to_datetime(
                search_criteria.car_rental.pickup_at,
            ),
            return_datetime=protobuf.protobuf_to_datetime(
                search_criteria.car_rental.return_at,
            ),
            driver_age=search_criteria.car_rental.driver_age,
        ),
    ]
