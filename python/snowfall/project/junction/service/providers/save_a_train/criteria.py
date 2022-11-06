import itertools
from collections.abc import Iterator

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.save_a_train import train_stations
from snowfall.project.junction.service.providers.save_a_train.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.time import date_to_age
from snowfall.stdlib.v1alpha import models_pb2


class CriteriaGenerator(object):
    def __init__(self, h3_mapping: h3.H3MappingRepository[train_stations.TrainStation]):
        self._mapping = h3_mapping

    def from_search_task(  # noqa: WPS210
        self,
        search_task: offers_amqp_pb2.TripOfferSearchTask,
    ) -> Iterator[amqp_pb2.SearchCriteriaTask]:
        segments = itertools.chain(*[tr.segments for tr in search_task.search.trips])

        for segment in segments:
            first_leg = more_itertools.first(segment.legs)
            last_leg = more_itertools.last(segment.legs)

            if first_leg.type != models_pb2.Schedule.TYPE_RAIL:
                continue

            origins = self._mapping.find_mapped_values(
                coordinates=first_leg.origin.coordinates,
                neighbour_search_radius=1,
            )
            destinations = self._mapping.find_mapped_values(
                coordinates=last_leg.destination.coordinates,
                neighbour_search_radius=1,
            )
            yield from (
                amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=[segment],
                    criteria=amqp_pb2.Criteria(
                        origin_id=start.identifier,
                        destination_id=end.identifier,
                        passengers_ages=[
                            date_to_age(
                                protobuf.protobuf_to_date(
                                    passenger.date_of_birth,
                                ),
                            )
                            for passenger in search_task.search.passengers
                        ],
                        departure_datetime=protobuf.datetime_to_protobuf_datetime(
                            protobuf.protobuf_to_datetime(
                                first_leg.departure_at,
                            ).astimezone(start.timezone),
                        ),
                        arrival_datetime=protobuf.datetime_to_protobuf_datetime(
                            protobuf.protobuf_to_datetime(
                                last_leg.arrival_at,
                            ).astimezone(end.timezone),
                        ),
                    ),
                    session_token=search_task.session_token,
                )
                for start, end in itertools.product(origins, destinations)
            )
