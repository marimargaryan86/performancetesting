import itertools

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.distribusion import stations
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.time import date_to_age
from snowfall.stdlib.v1alpha import models_pb2


class CriteriaGenerator(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[stations.Station]):
        self._mapping = h3_mapping

    def from_search_task(  # noqa: WPS210
        self,
        search_task: offers_amqp_pb2.TripOfferSearchTask,
    ) -> list[amqp_pb2.SearchCriteriaTask]:
        tasks: list[amqp_pb2.SearchCriteriaTask] = []

        for trip in search_task.search.trips:
            segments = trip.segments
            first_leg = more_itertools.first(more_itertools.first(segments).legs)
            last_leg = more_itertools.last(more_itertools.last(segments).legs)

            if first_leg.type != models_pb2.Schedule.TYPE_BUS:
                continue

            origins = self._mapping.find_mapped_values(
                coordinates=first_leg.origin.coordinates,
                neighbour_search_radius=1,
            )
            destinations = self._mapping.find_mapped_values(
                coordinates=last_leg.destination.coordinates,
                neighbour_search_radius=1,
            )

            tasks.extend(
                amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=segments,
                    criteria=amqp_pb2.Criteria(
                        origin_id=start.identifier,
                        destination_id=end.identifier,
                        passengers_age=[
                            date_to_age(
                                protobuf.protobuf_to_date(
                                    passenger.date_of_birth,
                                ),
                            )
                            for passenger in search_task.search.passengers
                        ],
                        outbound_departure=protobuf.date_to_protobuf(
                            protobuf.protobuf_to_datetime(
                                first_leg.departure_at,
                            ).astimezone(start.timezone),
                        ),
                    ),
                    session_token=search_task.session_token,
                )
                for start, end in itertools.product(origins, destinations)
            )

        return tasks
