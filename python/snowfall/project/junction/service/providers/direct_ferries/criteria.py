import itertools

import more_itertools

from snowfall.project.junction.go.service.offers.v1alpha import (
    amqp_pb2 as offers_amqp_pb2,
)
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

    def from_search_task(  # noqa: WPS210
        self,
        search_task: offers_amqp_pb2.TripOfferSearchTask,
    ) -> list[amqp_pb2.SearchCriteriaTask]:
        segments = itertools.chain(*[tr.segments for tr in search_task.search.trips])
        tasks: list[amqp_pb2.SearchCriteriaTask] = []

        for segment in segments:
            first_leg = more_itertools.first(segment.legs)
            last_leg = more_itertools.last(segment.legs)

            if first_leg.type != models_pb2.Schedule.TYPE_FERRY:
                continue

            origins = self._port_mapping.find_mapped_values(
                coordinates=first_leg.origin.coordinates,
                neighbour_search_radius=1,
            )
            destinations = self._port_mapping.find_mapped_values(
                coordinates=last_leg.destination.coordinates,
                neighbour_search_radius=1,
            )
            tasks.extend(
                amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=[segment],
                    criteria=amqp_pb2.Criteria(
                        origin_id=start.identifier,
                        destination_id=end.identifier,
                        route_id=self._routes.get_by_origin_destination(
                            origin=start.identifier,
                            destination=end.identifier,
                        ).route_id,
                        departure_datetime=protobuf.datetime_to_protobuf_datetime(
                            protobuf.protobuf_to_datetime(
                                first_leg.departure_at,
                            ).astimezone(start.timezone),
                        ),
                        passengers_ages=[
                            time.date_to_age(
                                protobuf.protobuf_to_date(pax.date_of_birth),
                            )
                            for pax in search_task.search.passengers
                        ],
                    ),
                    session_token=search_task.session_token,
                )
                for start, end in itertools.product(origins, destinations)
            )

        return tasks
