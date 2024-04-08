import dataclasses

from snowfall.project.junction.go.v1 import models_pb2 as common_pb2
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2


@dataclasses.dataclass(frozen=True)
class Criteria:
    search_id: str
    origin: common_pb2.Point
    destination: common_pb2.Point
    # TODO(regis.blanc): Implement the full criteria.


def search_criteria_generator(
    search: models_pb2.Search,
) -> list[Criteria]:
    # TODO(regis.blanc): Implement the full mapping.
    return [
        Criteria(
            search_id=search.id,
            origin=search.rail.origin,
            destination=search.rail.destination,
        ),
    ]
