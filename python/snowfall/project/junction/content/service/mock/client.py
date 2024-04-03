from __future__ import annotations

import dataclasses
import datetime
import itertools
import math
import zoneinfo
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, NamedTuple, Self

from geopy import distance

from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import fare_type_pb2
from snowfall.stdlib import h3, money
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2

_TRAVEL_SPEED = 880
_TAXI_TIME = 15
_NEAREST_MINUTE = 5
_LAYOVER = datetime.timedelta(hours=1)


class Airline(NamedTuple):
    iata: str
    name: str


_MARKETING_AIRLINE = Airline("XZ", "Snowfall Airlines")
_OPERATING_AIRLINE = Airline("XX", "Icey Airways")


@dataclasses.dataclass(frozen=True)
class Stop(h3.CoordinatesItem):
    name: str
    country_code: str
    rad_latitude: float
    rad_longitude: float


class StopRepository:
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
class Route:
    stops: Sequence[Stop]


class RouteRepository:
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


@dataclasses.dataclass(frozen=True)
class Company:
    flight_number: str
    name: str
    code: str


@dataclasses.dataclass(frozen=True)
class Segment:
    origin: Stop
    destination: Stop
    departure_at: datetime.datetime
    arrival_at: datetime.datetime
    marketed_by: Company
    operated_by: Company

    @classmethod
    def new(
        cls,
        origin: Stop,
        destination: Stop,
        departure_at: datetime.datetime,
    ) -> Self:
        return cls(
            origin=origin,
            destination=destination,
            departure_at=departure_at,
            arrival_at=departure_at + cls._calculate_travel_time(origin, destination),
            marketed_by=cls._generate_company(
                airline=_MARKETING_AIRLINE,
                origin=origin,
                destination=destination,
                departure_at=departure_at,
            ),
            operated_by=cls._generate_company(
                airline=_OPERATING_AIRLINE,
                origin=origin,
                destination=destination,
                departure_at=departure_at,
            ),
        )

    def get_next(self, destination: Stop) -> Segment:
        origin = self.destination
        departure_at = self.arrival_at + _LAYOVER
        arrival_at = departure_at + self._calculate_travel_time(origin, destination)

        return Segment(
            origin=origin,
            destination=destination,
            departure_at=departure_at,
            arrival_at=arrival_at,
            marketed_by=self._generate_company(
                airline=_MARKETING_AIRLINE,
                origin=origin,
                destination=destination,
                departure_at=departure_at,
            ),
            operated_by=self._generate_company(
                airline=_OPERATING_AIRLINE,
                origin=origin,
                destination=destination,
                departure_at=departure_at,
            ),
        )

    @classmethod
    def _generate_company(
        cls,
        airline: Airline,
        origin: Stop,
        destination: Stop,
        departure_at: datetime.datetime,
    ) -> Company:
        return Company(
            flight_number=cls._generate_flight_number(
                origin=origin,
                destination=destination,
                departure_at=departure_at,
                airline_iata=airline.iata,
            ),
            name=airline.name,
            code=airline.iata,
        )

    @classmethod
    def _generate_flight_number(
        cls,
        airline_iata: str,
        origin: Stop,
        destination: Stop,
        departure_at: datetime.datetime,
    ) -> str:
        route_signature = "{airline}:{origin}:{destination}:{time}".format(
            airline=airline_iata,
            origin=origin.identifier,
            destination=destination.identifier,
            time=departure_at.time(),
        )

        return str(hash(route_signature))[-3:].lstrip("0") or "1"

    @classmethod
    def _calculate_travel_time(
        cls,
        origin: Stop,
        destination: Stop,
    ) -> datetime.timedelta:
        kilometers = distance.distance(
            (origin.latitude, origin.longitude),
            (destination.latitude, destination.longitude),
        ).kilometers
        travel_minutes = _NEAREST_MINUTE * round(
            kilometers / _TRAVEL_SPEED * 60 / _NEAREST_MINUTE,
        )

        return datetime.timedelta(minutes=travel_minutes + _TAXI_TIME * 2)


@dataclasses.dataclass(frozen=True)
class Trip:
    segments: list[Segment]


@dataclasses.dataclass(frozen=True)
class Fare:
    reference: str
    price: money.Money
    brand_type: fare_type_pb2.FareType.ValueType
    brand_name: str


@dataclasses.dataclass(frozen=True)
class SearchResult:
    trips: list[Trip]
    fares: list[Fare]

    @classmethod
    def from_trips(cls, trips: Sequence[Trip]) -> Self:
        return cls(
            trips=list(trips),
            fares=FakeFareGenerator(trips).generate(),
        )


class FakeFareGenerator:
    _air_base_cost = 15
    _air_travel_cost = 0.00075
    _air_base_modifier = 2.1
    _air_fare_modifier = 0.065
    _round_trip_rebate = 0.7
    _air_fare_classes = (
        (fare_type_pb2.FARE_TYPE_ECONOMY, "Basic", 1.0),
        (fare_type_pb2.FARE_TYPE_ECONOMY, "Premium", 1.4),
        (fare_type_pb2.FARE_TYPE_BUSINESS, "Business", 2.7),
    )

    def __init__(
        self,
        trips: Sequence[Trip],
    ):
        self._trips = trips

    def generate(self) -> list[Fare]:
        return [
            Fare(
                reference="foo",
                price=money.from_string(
                    str(self._calculate_trips_price(markup)),
                    currency=money.Currency("EUR"),
                ),
                brand_type=fare_type,
                brand_name=marketing_name,
            )
            for fare_type, marketing_name, markup in self._air_fare_classes
        ]

    def _get_rebate(self) -> float:
        if self._is_round_trip():
            return self._round_trip_rebate

        return 1

    def _is_round_trip(self) -> bool:
        if len(self._trips) < 2:
            return False

        first_segment = self._trips[0].segments[0]
        last_segment = self._trips[-1].segments[-1]

        return first_segment.origin.identifier == last_segment.destination.identifier

    def _calculate_trips_price(self, markup: float) -> int:
        return round(
            sum(
                self._calculate_segment_price(segment, markup)
                for trip in self._trips
                for segment in trip.segments
            )
            * self._get_rebate(),
        )

    def _calculate_segment_price(
        self,
        segment: Segment,
        markup: float,
    ) -> float:
        travel_time = segment.arrival_at - segment.departure_at
        base_price = (
            self._air_base_cost
            + (travel_time.total_seconds() * self._air_travel_cost)
            ** self._air_base_modifier
        )

        return (
            base_price * travel_time.total_seconds() ** self._air_fare_modifier * markup
        )


class MockClient:
    def __init__(self, route_repository: RouteRepository):
        self._routes = route_repository

    def find_one_way(
        self,
        one_way: trips_pb2.SearchTripsRequest.OneWay,
    ) -> list[SearchResult]:
        routes = self._routes.find_routes(
            origin=one_way.criterion.origin_identifier,
            destination=one_way.criterion.destination_identifier,
        )
        departure_at = _make_mock_time(one_way.criterion.departure_date)

        return [
            SearchResult.from_trips(
                [Trip(segments=_make_segments(route, departure_at))],
            )
            for route in routes
        ]

    def find_round_trip(
        self,
        round_trip: trips_pb2.SearchTripsRequest.RoundTrip,
    ) -> list[SearchResult]:
        routes = self._routes.find_routes(
            origin=round_trip.criterion.origin_identifier,
            destination=round_trip.criterion.destination_identifier,
        )
        departure_at = _make_mock_time(round_trip.criterion.departure_date)
        return_at = _make_mock_time(round_trip.return_date)

        return [
            SearchResult.from_trips(
                [
                    Trip(segments=_make_segments(outbound_route, departure_at)),
                    Trip(segments=_make_segments(inbound_route[::-1], return_at)),
                ],
            )
            for outbound_route, inbound_route in itertools.product(routes, routes)
        ]

    def find_multi_city(
        self,
        multi_city: trips_pb2.SearchTripsRequest.MultiCity,
    ) -> list[SearchResult]:
        criteria_trips = []

        for criterion in multi_city.criteria:
            routes = self._routes.find_routes(
                origin=criterion.origin_identifier,
                destination=criterion.destination_identifier,
            )
            departure_at = _make_mock_time(criterion.departure_date)
            criteria_trips.append(
                [
                    Trip(segments=_make_segments(route, departure_at))
                    for route in routes
                ],
            )

        return [
            SearchResult.from_trips(trips=trips)
            for trips in itertools.product(*criteria_trips)
        ]


def _make_mock_time(date: date_pb2.Date) -> datetime.datetime:
    return datetime.datetime.combine(
        protobuf.protobuf_to_date(date),
        datetime.time(hour=8),
        tzinfo=datetime.UTC,
    )


def _make_segments(
    route: Sequence[Stop],
    departure_at: datetime.datetime,
) -> list[Segment]:
    segments: list[Segment] = []

    for origin, destination in itertools.pairwise(route):
        try:
            segments.append(segments[-1].get_next(destination))
        except IndexError:
            segments.append(
                Segment.new(
                    origin=origin,
                    destination=destination,
                    departure_at=departure_at,
                ),
            )

    return segments
