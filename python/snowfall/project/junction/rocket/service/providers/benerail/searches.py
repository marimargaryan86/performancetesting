from __future__ import annotations

import dataclasses
import datetime
import functools
import secrets
import zoneinfo
from collections.abc import Collection, Iterable, Sequence

from geopy.distance import geodesic
from google.protobuf import message

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.rocket.service.providers.benerail import (
    constant,
    id_mapping,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.benerail.helper_functions import (
    normalize_datetime,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import h3, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2

_TOKEN_LENGTH = 32


@dataclasses.dataclass(frozen=True)
class Criteria(message.Message):
    origin: str
    destination: str
    passenger_dobs: Sequence[datetime.date]
    outbound_departure_datetime: datetime.datetime
    trip_sequence: int
    session_token: str
    inbound_departure_datetime: datetime.datetime | None = None
    outward_offer_search_id: str | None = None
    return_departure_after: datetime.datetime | None = None
    outbound_id: str | None = None


def cache_key(search: Criteria) -> str:
    return string.uuid()


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
        _id_mapping: id_mapping.IdMappingRepository[train_stations.TrainStation],
    ):
        self._mapping = h3_mapping
        self._id_mapping = _id_mapping

    def criteria_task_generator(
        self,
        search: models_pb2.Search,
    ) -> list[Criteria]:
        origins = self._get_stations(
            search.rail.origin.coordinates,
        )
        destinations = self._get_stations(
            search.rail.destination.coordinates,
        )
        if not origins or not destinations:
            return []
        return create_criteria_time_windows(
            frozenset(origins),
            frozenset(destinations),
            search,
        )

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


def _get_provider_ids(
    provider_ids: Iterable[offers_pb2.ProviderIds],
) -> Iterable[str] | None:
    for places_ids in provider_ids:
        if places_ids.provider_id == str(constant.PROVIDER_ID):
            return places_ids.place_ids
    return None


def _generate_inbound_search_criteria(
    search: models_pb2.Search,
    origin: str,
    destination: str,
    timezone_destination: zoneinfo.ZoneInfo,
    timezone_origin: zoneinfo.ZoneInfo,
) -> list[Criteria]:
    timestamps = find_time_windows(
        None,  # Placeholder for future logic
        departure_after=normalize_datetime(
            protobuf.protobuf_to_datetime(search.rail.return_date),
            timezone_origin,
        ),
        timezone=timezone_origin,
    )

    trip_sequence = 2
    return _generate_search_criteria(
        timestamps,
        search,
        origin,
        destination,
        trip_sequence,
    )


def _generate_outbound_search_criteria(
    search: models_pb2.Search,
    origin: str,
    destination: str,
    timezone_destination: zoneinfo.ZoneInfo,
    timezone_origin: zoneinfo.ZoneInfo,
) -> list[Criteria]:
    departure_after = normalize_datetime(
        protobuf.protobuf_to_datetime(search.rail.departure_after),
        timezone_origin,
    )
    departure_before = (
        protobuf.protobuf_to_datetime(search.rail.departure_before)
        if search.rail.HasField("departure_before")
        else None
    )
    return_departure_after = (
        normalize_datetime(
            protobuf.protobuf_to_datetime(search.rail.return_date),
            timezone_destination,
        )
        if search.rail.HasField("departure_before")
        else None
    )

    timestamps = find_time_windows(
        departure_before,
        departure_after,
        timezone=timezone_origin,
    )
    trip_sequence = 1
    return _generate_search_criteria(
        timestamps,
        search,
        origin,
        destination,
        trip_sequence,
        return_departure_after,
    )


def _generate_search_criteria(
    timestamps: Sequence[datetime.datetime],
    search: models_pb2.Search,
    destination: str,
    origin: str,
    trip_sequence: int,
    return_departure_after: datetime.datetime | None = None,
) -> list[Criteria]:
    passenger_dobs = [
        protobuf.protobuf_to_date(passenger.date_of_birth)
        for passenger in search.rail.passengers
    ]

    return [
        Criteria(
            origin=origin,
            destination=destination,
            passenger_dobs=passenger_dobs,
            outward_offer_search_id=search.rail.outbound_search_result_id,
            return_departure_after=return_departure_after,
            outbound_departure_datetime=timestamp,
            trip_sequence=trip_sequence,
            session_token=secrets.token_urlsafe(_TOKEN_LENGTH),
        )
        for timestamp in timestamps
    ]


def create_criteria_time_windows(
    origins: Collection[train_stations.TrainStation],
    destinations: Collection[train_stations.TrainStation],
    search: models_pb2.Search,
) -> list[Criteria]:
    origin_id, origin_timezone = _find_nearest_provider_place(
        origins,
        search.rail.origin.coordinates,
    )
    destination_id, destination_timezone = _find_nearest_provider_place(
        destinations,
        search.rail.destination.coordinates,
    )

    if search.rail.outbound_search_result_id:
        criteria_func = _generate_inbound_search_criteria
    else:
        criteria_func = _generate_outbound_search_criteria

    return criteria_func(
        search,
        origin_id,
        destination_id,
        origin_timezone,
        destination_timezone,
    )


def find_time_windows(
    departure_before: datetime.datetime | None,
    departure_after: datetime.datetime,
    timezone: zoneinfo.ZoneInfo,
) -> list[datetime.datetime]:
    timestamps = []
    if departure_before:
        departure_before = departure_before.astimezone(timezone)
    else:
        departure_before = departure_after + datetime.timedelta(days=1)
        departure_before = departure_before.replace(hour=0)
        departure_before = departure_before.astimezone(timezone)

    while departure_after < departure_before:
        timestamps.append(departure_after)
        departure_after += datetime.timedelta(hours=2)

    return timestamps
