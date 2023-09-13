import dataclasses
import datetime
import itertools
import math
import zoneinfo
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any

from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.v1 import segment_type_pb2
from snowfall.stdlib import h3, money
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


class FakeFareGenerator(object):
    _air_base_cost = 15
    _air_travel_cost = 0.00075
    _air_base_modifier = 2.1
    _air_fare_modifier = 0.065
    _round_trip_rebate = 0.7
    _air_fare_classes = (
        ("Basic", 1.0),
        ("Premium", 1.4),
        ("Business", 2.7),
    )

    def __init__(
        self,
        trips: Sequence[trips_pb2.Trip],
    ):
        self._trips = trips

    def generate(self) -> list[trips_pb2.Fare]:
        return [
            trips_pb2.Fare(
                reference="foo",
                price=money.from_string(
                    str(self._calculate_trips_price(markup)),
                    currency=money.Currency("EUR"),
                ).protobuf(),
                brand_name=brand,
            )
            for brand, markup in self._air_fare_classes
        ]

    def _get_rebate(self) -> float:
        if self._is_round_trip():
            return self._round_trip_rebate

        return 1

    def _is_round_trip(self) -> bool:
        if len(self._trips) < 2:
            return False

        first_segments = self._trips[0].segments
        last_segments = self._trips[-1].segments
        first_leg = first_segments[0].legs[0]
        last_leg = last_segments[-1].legs[-1]

        return first_leg.origin.ref == last_leg.destination.ref

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
        segment: trips_pb2.Segment,
        markup: float,
    ) -> float:
        travel_time = protobuf.protobuf_to_datetime(
            segment.legs[-1].arrival_at,
        ) - protobuf.protobuf_to_datetime(segment.legs[0].departure_at)
        base_price = (
            self._air_base_cost
            + (travel_time.total_seconds() * self._air_travel_cost)
            ** self._air_base_modifier
        )

        return (
            base_price * travel_time.total_seconds() ** self._air_fare_modifier * markup
        )


class Trips(object):
    def __init__(self, route_repository: RouteRepository):
        self._routes = route_repository

    async def find(
        self,
        trip_request: trips_pb2.SearchTripsRequest,
    ) -> trips_pb2.SearchTripsResponse:
        match trip_request.WhichOneof("search_mode"):
            case "one_way":
                return trips_pb2.SearchTripsResponse(
                    results=self._find_one_ways(trip_request.one_way.criterion),
                )
            case "round_trip":
                return trips_pb2.SearchTripsResponse(
                    results=self._find_round_trips(trip_request.round_trip),
                )
            case "multi_city":
                return trips_pb2.SearchTripsResponse(
                    results=self._find_multi_city(trip_request.multi_city),
                )

        return trips_pb2.SearchTripsResponse()

    def _find_one_ways(
        self,
        criterion: trips_pb2.SearchTripsRequest.Criterion,
    ) -> list[trips_pb2.Result]:
        routes = self._routes.find_routes(
            origin=criterion.origin_identifier,
            destination=criterion.destination_identifier,
        )
        departure_at = datetime.datetime.combine(
            protobuf.protobuf_to_date(criterion.departure_date),
            datetime.time(hour=8),
            tzinfo=datetime.UTC,
        )

        return [
            _generate_result_for_trips(
                [trips_pb2.Trip(segments=_make_segments(route, departure_at))],
            )
            for route in routes
        ]

    def _find_round_trips(
        self,
        round_trip: trips_pb2.SearchTripsRequest.RoundTrip,
    ) -> list[trips_pb2.Result]:
        routes = self._routes.find_routes(
            origin=round_trip.criterion.origin_identifier,
            destination=round_trip.criterion.destination_identifier,
        )
        departure_at = datetime.datetime.combine(
            protobuf.protobuf_to_date(round_trip.criterion.departure_date),
            datetime.time(hour=8),
            tzinfo=datetime.UTC,
        )
        return_at = datetime.datetime.combine(
            protobuf.protobuf_to_date(round_trip.return_date),
            datetime.time(hour=8),
            tzinfo=datetime.UTC,
        )

        return [
            _generate_result_for_trips(
                [
                    trips_pb2.Trip(
                        segments=_make_segments(outbound_route, departure_at),
                    ),
                    trips_pb2.Trip(
                        segments=_make_segments(inbound_route[::-1], return_at),
                    ),
                ],
            )
            for outbound_route, inbound_route in itertools.product(routes, routes)
        ]

    def _find_multi_city(
        self,
        multi_city: trips_pb2.SearchTripsRequest.MultiCity,
    ) -> list[trips_pb2.Result]:
        criteria_trips = []

        for criterion in multi_city.criteria:
            routes = self._routes.find_routes(
                origin=criterion.origin_identifier,
                destination=criterion.destination_identifier,
            )
            departure_at = datetime.datetime.combine(
                protobuf.protobuf_to_date(criterion.departure_date),
                datetime.time(hour=8),
                tzinfo=datetime.UTC,
            )
            criteria_trips.append(
                [
                    trips_pb2.Trip(
                        segments=_make_segments(route, departure_at),
                    )
                    for route in routes
                ],
            )

        return [
            _generate_result_for_trips(trips)
            for trips in itertools.product(*criteria_trips)
        ]


def _make_segments(
    route: Sequence[Stop],
    departure_at: datetime.datetime,
) -> list[trips_pb2.Segment]:
    travel_time = FakeTravelTime(
        departure_at=departure_at,
        start=route[0],
    )

    return [
        _make_segment(
            travel_time=travel_time,
            origin=origin,
            destination=destination,
        )
        for origin, destination in itertools.pairwise(route)
    ]


def _make_segment(
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


def _generate_result_for_trips(
    trips: Sequence[trips_pb2.Trip],
) -> trips_pb2.Result:
    return trips_pb2.Result(
        trips=trips,
        fares=FakeFareGenerator(trips).generate(),
    )
