import dataclasses
import datetime

from google.protobuf import message

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf


@dataclasses.dataclass(frozen=True)
class Criteria(message.Message):
    search_id: str
    origin: common_pb2.Point
    destination: common_pb2.Point
    pickup_datetime: datetime.datetime
    return_datetime: datetime.datetime
    driver_age: int


def search_criteria_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    return [
        Criteria(
            search_id=search.id,
            origin=search.car_rental.origin,
            destination=search.car_rental.destination,
            pickup_datetime=protobuf.protobuf_to_datetime(
                search.car_rental.pickup_at,
            ),
            return_datetime=protobuf.protobuf_to_datetime(
                search.car_rental.return_at,
            ),
            driver_age=search.car_rental.driver_age,
        ),
    ]
