import dataclasses
import datetime
import itertools
import math
import zoneinfo
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any

from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2


@dataclasses.dataclass(frozen=True)
class Stop(h3.CoordinatesItem):
    name: str
    country_code: str
    rad_latitude: float
    rad_longitude: float


class StopRepository(object):
    def __init__(
        self,
        stops: Iterable[Mapping[str, Any]],
    ):
        self._stops = {
            stop["ref"]: Stop(
                identifier=stop["ref"],
                latitude=stop["lat"],
                longitude=stop["lon"],
                timezone=zoneinfo.ZoneInfo(stop["tz"]),
                country_code=stop["country"],
                name=stop["name"],
                rad_latitude=math.radians(stop["lat"]),
                rad_longitude=math.radians(stop["lon"]),
            )
            for stop in stops
        }

    def all_(self) -> Iterator[Stop]:
        yield from self._stops.values()

    def get(self, identifier: str) -> Stop:
        return self._stops[identifier]


@dataclasses.dataclass(frozen=True)
class Route(object):
    stops: Sequence[Stop]


class RouteRepository(object):
    def __init__(
        self,
        stop_repository: StopRepository,
        routes: Iterable[Iterable[str]],
    ):
        self._routes = [
            [stop_repository.get(stop) for stop in route] for route in routes
        ]

    def find_routes(self, origin: str, destination: str) -> list[Sequence[Stop]]:
        return [
            route
            for route in self._routes
            if route[0].identifier == origin and route[-1].identifier == destination
        ]


class FakeTravelTime(object):
    _earth_radius = 6373.0
    _travel_speed = 880
    _taxi_time = 15
    _nearest_minute = 5
    _layover = datetime.timedelta(hours=1)

    def __init__(self, departure_at: datetime.datetime, start: Stop):
        self._start = start
        self._last_departure_at = departure_at

    def make_time_tuple(
        self,
        stop: Stop,
    ) -> tuple[datetime.datetime, datetime.datetime]:
        last_departure_at = self._last_departure_at
        next_departure_at = self._last_departure_at + self._calculate_travel_time(stop)
        self._start = stop
        self._last_departure_at = next_departure_at + self._layover

        return last_departure_at, next_departure_at

    def _calculate_travel_time(self, stop: Stop) -> datetime.timedelta:
        distance = self._calculate_distance(stop)
        travel_minutes = self._nearest_minute * round(
            distance / self._travel_speed * 60 / self._nearest_minute,
        )

        return datetime.timedelta(minutes=travel_minutes + self._taxi_time * 2)

    def _calculate_distance(self, stop: Stop) -> float:
        arc = (
            math.sin((stop.rad_latitude - self._start.rad_latitude) / 2) ** 2
            + math.cos(self._start.rad_latitude)
            * math.cos(stop.rad_latitude)
            * math.sin(stop.rad_longitude - self._start.rad_longitude / 2) ** 2
        )
        curve = 2 * math.atan2(
            math.sqrt(arc),
            math.sqrt(1 - arc),
        )

        return self._earth_radius * curve


class Trips(object):
    def __init__(self, route_repository: RouteRepository):
        self._routes = route_repository

    async def find(
        self,
        trip_request: trips_pb2.SearchTripsRequest,
    ) -> trips_pb2.SearchTripsResponse:
        criterion = trip_request.criterion[0]
        routes = self._routes.find_routes(
            origin=criterion.origin_identifier,
            destination=criterion.destination_identifier,
        )
        departure_at = datetime.datetime.combine(
            protobuf.protobuf_to_date(criterion.departure_date),
            datetime.time(hour=8),
            tzinfo=datetime.UTC,
        )

        return trips_pb2.SearchTripsResponse(
            trips=[
                self._make_trip(
                    departure_at=departure_at,
                    route=route,
                )
                for route in routes
            ],
        )

    def _make_trip(
        self,
        departure_at: datetime.datetime,
        route: Sequence[Stop],
    ) -> trips_pb2.Trip:
        travel_time = FakeTravelTime(
            departure_at=departure_at,
            start=route[0],
        )
        return trips_pb2.Trip(
            segments=[
                self._make_segment(
                    travel_time=travel_time,
                    origin=origin,
                    destination=destination,
                )
                for origin, destination in itertools.pairwise(route)
            ],
        )

    def _make_segment(
        self,
        travel_time: FakeTravelTime,
        origin: Stop,
        destination: Stop,
    ) -> trips_pb2.Segment:
        departure_at, arrival_at = travel_time.make_time_tuple(destination)

        return trips_pb2.Segment(
            legs=[
                trips_pb2.Leg(
                    origin=trips_pb2.Location(
                        ref=origin.identifier,
                        name=origin.name,
                        coordinates=latlng_pb2.LatLng(
                            latitude=origin.latitude,
                            longitude=origin.longitude,
                        ),
                    ),
                    destination=trips_pb2.Location(
                        ref=destination.identifier,
                        name=destination.name,
                        coordinates=latlng_pb2.LatLng(
                            latitude=destination.latitude,
                            longitude=destination.longitude,
                        ),
                    ),
                    departure_at=protobuf.datetime_to_protobuf_datetime(departure_at),
                    arrival_at=protobuf.datetime_to_protobuf_datetime(arrival_at),
                ),
            ],
            type=segment_type_pb2.SEGMENT_TYPE_FLIGHT,
        )
