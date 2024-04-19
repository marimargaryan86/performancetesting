from __future__ import annotations

import dataclasses
import datetime
import functools
import secrets
import zoneinfo
from collections.abc import Iterable, Sequence

import grpc
from geopy.distance import geodesic
from google.protobuf import message

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.rocket.service.places.v1alpha import (
    places_pb2,
    places_pb2_grpc,
)
from snowfall.project.junction.rocket.service.providers.benerail import (
    constant,
    train_stations,
)
from snowfall.project.junction.rocket.service.providers.benerail.helper_functions import (
    normalize_datetime,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
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


class PlaceNotFoundError(Exception):
    """Raised when place is not found."""


class StationNotFoundError(Exception):
    """Raised when there is no capability for the provider."""


class CriteriaGenerator:
    def __init__(
        self,
        places: places_pb2_grpc.PlacesServiceStub,
    ):
        self._places = places
        self._logger = stdout.get_logger()

    async def get_station(self, place_id: str) -> train_stations.TrainStation:
        try:
            place = (
                await self._places.GetPlace(
                    places_pb2.GetPlaceRequest(id=place_id),
                )
            ).place
        except grpc.aio.AioRpcError as err:
            if err.code() == grpc.StatusCode.NOT_FOUND:
                raise PlaceNotFoundError(place_id) from err
            raise

        station_id = place.search_capabilities.rail.get(str(constant.PROVIDER_ID))
        if not station_id:
            raise StationNotFoundError(place_id)

        return train_stations.TrainStation(
            name=place.name,
            identifier=station_id,
            latitude=place.coordinates.latitude,
            longitude=place.coordinates.longitude,
            timezone=zoneinfo.ZoneInfo(place.time_zone),
        )

    async def criteria_task_generator(
        self,
        search: models_pb2.Search,
    ) -> list[Criteria]:
        try:
            origin = await self.get_station(search.rail.origin_id)
        except (PlaceNotFoundError, StationNotFoundError):
            self._logger.exception("Unable to retrieve origin station id.")
            return []

        try:
            destination = await self.get_station(search.rail.destination_id)
        except (PlaceNotFoundError, StationNotFoundError):
            self._logger.exception("Unable to retrieve destination station id.")
            return []

        return create_criteria_time_windows(
            origin=origin,
            destination=destination,
            search=search,
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
        timestamps=timestamps,
        search=search,
        origin=origin,
        destination=destination,
        trip_sequence=trip_sequence,
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
        timestamps=timestamps,
        search=search,
        origin=origin,
        destination=destination,
        trip_sequence=trip_sequence,
        return_departure_after=return_departure_after,
    )


def _generate_search_criteria(
    timestamps: Sequence[datetime.datetime],
    search: models_pb2.Search,
    origin: str,
    destination: str,
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
            outward_offer_search_id=search.rail.outbound_offer_id,
            return_departure_after=return_departure_after,
            outbound_departure_datetime=timestamp,
            trip_sequence=trip_sequence,
            session_token=secrets.token_urlsafe(_TOKEN_LENGTH),
        )
        for timestamp in timestamps
    ]


def create_criteria_time_windows(
    origin: train_stations.TrainStation,
    destination: train_stations.TrainStation,
    search: models_pb2.Search,
) -> list[Criteria]:
    if search.rail.outbound_offer_id:
        criteria_func = _generate_inbound_search_criteria
    else:
        criteria_func = _generate_outbound_search_criteria

    return criteria_func(
        search=search,
        origin=origin.identifier,
        destination=destination.identifier,
        timezone_origin=origin.timezone,
        timezone_destination=destination.timezone,
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
