import datetime
import functools
import zoneinfo
from collections.abc import Iterable

from geopy.distance import geodesic

from snowfall.project.junction.rocket.service.providers.silverrail import (
    criteria,
    train_stations,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

MAX_SEARCH_RANGE_SECONDS = 24 * 3600  # noqa: WPS432


class InvalidSearchRequestError(Exception):
    """Thrown if the search request is invalid."""


def _calculate_distance_geopy(
    p1: tuple[float, float],
    p2: train_stations.TrainStation,
) -> float:
    """Return the great circle distance in meters between two points using geopy."""
    station = (p2.latitude, p2.longitude)
    return geodesic(p1, station).meters


def _find_nearest_provider_place(
    stations: Iterable[train_stations.TrainStation],
    coordinates: latlng_pb2.LatLng,
) -> tuple[str, zoneinfo.ZoneInfo]:
    coords = coordinates.latitude, coordinates.longitude
    nearest_station = min(
        stations,
        key=functools.partial(_calculate_distance_geopy, coords),
    )

    return nearest_station.identifier, nearest_station.timezone


class CriteriaGenerator:
    def __init__(
        self,
        h3_mapping: h3.H3MappingRepository[train_stations.TrainStation],
    ):
        self._mapping = h3_mapping

    async def criteria_task_generator(
        self,
        search: models_pb2.Search,
    ) -> list[criteria.Criteria]:
        origins = self._get_stations(
            search.rail.origin.coordinates,
        )
        destinations = self._get_stations(
            search.rail.destination.coordinates,
        )
        if not origins or not destinations:
            return []
        origin_id, _origin_timezone = _find_nearest_provider_place(
            origins,
            search.rail.origin.coordinates,
        )
        destination_id, _destination_timezone = _find_nearest_provider_place(
            destinations,
            search.rail.destination.coordinates,
        )

        outbound_departure_after = protobuf.protobuf_to_datetime(
            search.rail.departure_after,
        )
        if search.rail.HasField("departure_before"):
            outbound_departure_before = protobuf.protobuf_to_datetime(
                search.rail.departure_before,
            )
        else:
            # If there's no constraint on departure before, we assume it's end of day.
            outbound_departure_before = outbound_departure_after + datetime.timedelta(
                days=1,
            )
            outbound_departure_before = outbound_departure_before.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        if outbound_departure_before <= outbound_departure_after:
            raise InvalidSearchRequestError(
                "outbound_departure_before cannot be earlier than outbound_departure_after",
            )

        search_range = (
            outbound_departure_before - outbound_departure_after
        ).total_seconds()

        if search_range > MAX_SEARCH_RANGE_SECONDS:
            raise InvalidSearchRequestError(
                "outbound_departure_before must be within one day of outbound_departure_after",
            )

        passenger_dobs = [
            protobuf.protobuf_to_date(passenger.date_of_birth)
            for passenger in search.rail.passengers
        ]

        return [
            criteria.Criteria(
                search_id=search.id,
                origin=origin_id,
                destination=destination_id,
                passenger_dobs=passenger_dobs,
                outbound_departure_after=outbound_departure_after,
                outbound_departure_before=outbound_departure_before,
            ),
        ]

    def _get_stations(
        self,
        coordinates: latlng_pb2.LatLng,
    ) -> set[train_stations.TrainStation]:
        self._mapping.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=1,
        )

        return self._mapping.find_mapped_values(
            coordinates=coordinates,
            neighbour_search_radius=1,
        )
