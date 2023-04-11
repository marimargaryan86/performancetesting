from typing import Iterator, Sequence

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.provider import segment_grouper
from snowfall.project.junction.service.providers.direct_ferries import port, route
from snowfall.project.junction.service.providers.direct_ferries.v1alpha import amqp_pb2
from snowfall.stdlib import h3, time
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2


class CriteriaGenerator(object):
    def __init__(
        self,
        h3_port_mapping: h3.H3MappingRepository[port.Port],
        routes: route.RouteRepository,
    ):
        self._port_mapping = h3_port_mapping
        self._routes = routes
        self._grouper = segment_grouper.SegmentGrouper(h3_port_mapping)

    def from_search_task(
        self,
        search: offer_models_pb2.TripOfferSearch,
    ) -> list[amqp_pb2.SearchCriteriaTask]:
        sub_trips = self._grouper.trips_to_sub_trips(
            trips=search.trips,
            type_filter=models_pb2.Schedule.TYPE_FERRY,
        )
        tasks: list[amqp_pb2.SearchCriteriaTask] = []

        for trip_criteria in segment_grouper.generate_trip_criteria(sub_trips):
            tasks.extend(
                self._generate_search_criteria(
                    trip_criteria=trip_criteria,
                    passenger_ages=[
                        time.date_to_age(
                            protobuf.protobuf_to_date(pax.date_of_birth),
                        )
                        for pax in search.passengers
                    ],
                ),
            )

        return tasks

    def _generate_search_criteria(
        self,
        trip_criteria: segment_grouper.TripCriteria,
        passenger_ages: Sequence[int],
    ) -> Iterator[amqp_pb2.SearchCriteriaTask]:
        for origin, destination in trip_criteria.get_combinations():
            task = amqp_pb2.SearchCriteriaTask(
                segments=trip_criteria.outbound.segments,
                criteria=amqp_pb2.Criteria(
                    origin_id=origin,
                    destination_id=destination,
                    outbound_route_id=self._routes.get_by_origin_destination(
                        origin=origin,
                        destination=destination,
                    ).route_id,
                    outbound_departure_datetime=protobuf.datetime_to_protobuf_datetime(
                        trip_criteria.outbound.departure,
                    ),
                    passengers_ages=passenger_ages,
                ),
            )

            if trip_criteria.inbound:
                task.segments.extend(
                    trip_criteria.inbound.segments,
                )
                task.criteria.inbound_departure_datetime.CopyFrom(
                    protobuf.datetime_to_protobuf_datetime(
                        trip_criteria.inbound.departure,
                    ),
                )
                task.criteria.inbound_route_id = self._routes.get_by_origin_destination(
                    origin=destination,
                    destination=origin,
                ).route_id

            yield task
