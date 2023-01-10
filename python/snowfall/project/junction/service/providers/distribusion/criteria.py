import itertools
from typing import Collection, Sequence

import more_itertools

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2 as offers_amqp_pb2
from snowfall.project.junction.service.providers.distribusion import stations
from snowfall.project.junction.service.providers.distribusion.v1alpha import amqp_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.time import date_to_age
from snowfall.stdlib.v1alpha import models_pb2

_MAX_STATIONS = 8


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

            origin_groups = self._group_stations(origins)
            dest_groups = self._group_stations(destinations)

            tasks.extend(
                amqp_pb2.SearchCriteriaTask(
                    offer_search_id=search_task.offer_search_id,
                    segments=segments,
                    criteria=amqp_pb2.Criteria(
                        origin_ids=[station.identifier for station in start],
                        destination_ids=[station.identifier for station in end],
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
                            ).astimezone(start[0].timezone),
                        ),
                    ),
                    session_token=search_task.session_token,
                )
                for start, end in itertools.product(origin_groups, dest_groups)
            )

        return tasks

    def _split_stations(
        self,
        station_list: Sequence[stations.Station],
        max_cnt: int,
    ) -> Sequence[Sequence[stations.Station]]:
        groups = list[list[stations.Station]]()

        for station_ind, station in enumerate(station_list):
            group_ind = station_ind // max_cnt

            if group_ind >= len(groups):
                groups.append(list[stations.Station]())

            groups[group_ind].append(station)

        return groups

    def _group_stations(
        self,
        station_set: Collection[stations.Station],
    ) -> Sequence[Sequence[stations.Station]]:
        station_list = sorted(station_set, key=lambda station: station.identifier)
        total_count = len(station_list)
        group_count = total_count // _MAX_STATIONS

        if total_count % _MAX_STATIONS > 0:
            group_count += 1

        count_per_group = total_count // group_count

        if total_count % group_count > 0:
            count_per_group += 1

        return self._split_stations(station_list, count_per_group)
