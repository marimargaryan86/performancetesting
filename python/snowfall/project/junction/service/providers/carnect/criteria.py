from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.service.providers.carnect.v1 import amqp_pb2
from snowfall.stdlib.format import protobuf


def simple_search_criteria_task_generator(
    search: offers_pb2.SimpleTripOfferSearch,
) -> list[amqp_pb2.Criteria]:
    if models_pb2.Schedule.TYPE_CAR not in search.allowed_segment_types:
        return []

    return [
        amqp_pb2.Criteria(
            origin=search.origin.coordinates,
            destination=search.destination.coordinates,
            passengers_count=len(search.passengers),
            pick_up_datetime=protobuf.datetime_to_protobuf_datetime(
                protobuf.protobuf_to_datetime(
                    search.departure_at,
                ),
            ),
            return_datetime=protobuf.datetime_to_protobuf_datetime(
                protobuf.protobuf_to_datetime(
                    search.arrival_at,
                ),
            ),
        ),
    ]


def simple_search_criteria_generator(
    search_task: amqp_pb2.Criteria,
) -> amqp_pb2.Criteria:
    return search_task
