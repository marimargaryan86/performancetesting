import itertools
from typing import Collection, Sequence

import more_itertools

from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
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

    def from_search(  # noqa: WPS210
        self,
        search: offer_models_pb2.TripOfferSearch,
    ) -> list[amqp_pb2.SearchCriteriaTask]:
        tasks: list[amqp_pb2.SearchCriteriaTask] = []

        for trip in search.trips:
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

            origin_cities = self._station_into_city(origins)
            dest_cities = self._station_into_city(destinations)

            tasks.extend(
                amqp_pb2.SearchCriteriaTask(
                    segments=segments,
                    criteria=amqp_pb2.Criteria(
                        origin_ids=[start],
                        destination_ids=[end],
                        passengers_age=[
                            date_to_age(
                                protobuf.protobuf_to_date(
                                    passenger.date_of_birth,
                                ),
                            )
                            for passenger in search.passengers
                        ],
                        outbound_departure=protobuf.date_to_protobuf(
                            protobuf.protobuf_to_datetime(
                                first_leg.departure_at,
                            ).astimezone(next(iter(origins)).timezone),
                        ),
                    ),
                )
                for start, end in itertools.product(origin_cities, dest_cities)
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

    def _station_into_city(
        self,
        station_set: Collection[stations.Station],
    ) -> Sequence[str]:
        city_set = {station.identifier[:5] for station in station_set}
        return list(city_set)
