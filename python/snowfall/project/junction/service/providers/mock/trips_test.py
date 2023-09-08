import datetime
from collections.abc import Sequence
from typing import Any, cast

import pytest

from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.project.junction.service.providers.mock import trips
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem


@pytest.fixture()
def stop_repository() -> trips.StopRepository:
    return trips.StopRepository(
        stops=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(__name__).load("stops.json"),
        ),
    )


@pytest.fixture()
def route_repository(stop_repository: trips.StopRepository) -> trips.RouteRepository:
    return trips.RouteRepository(
        stop_repository=stop_repository,
        routes=cast(
            list[list[str]],
            filesystem.PkgLoader(__name__).load("routes.json"),
        ),
    )


@pytest.fixture()
def trip_searcher(route_repository: trips.RouteRepository) -> trips.Trips:
    return trips.Trips(route_repository=route_repository)


@pytest.fixture()
def passengers() -> list[trips_pb2.SearchTripsRequest.Passenger]:
    return [
        trips_pb2.SearchTripsRequest.Passenger(
            date_of_birth=protobuf.date_to_protobuf(
                datetime.date(year=1987, month=5, day=24),
            ),
        ),
    ]


@pytest.fixture()
async def one_way_response(
    trip_searcher: trips.Trips,
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(
        trips_pb2.SearchTripsRequest(
            one_way=trips_pb2.SearchTripsRequest.OneWay(
                criterion=_generate_criterion(),
            ),
            passengers=passengers,
        ),
    )


@pytest.fixture()
async def round_trip_response(
    trip_searcher: trips.Trips,
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(
        trips_pb2.SearchTripsRequest(
            round_trip=trips_pb2.SearchTripsRequest.RoundTrip(
                criterion=_generate_criterion(),
                return_date=protobuf.date_to_protobuf(
                    datetime.date(year=2023, month=9, day=10),
                ),
            ),
            passengers=passengers,
        ),
    )


@pytest.fixture()
def multi_city_criteria() -> list[trips_pb2.SearchTripsRequest.Criterion]:
    return [
        _generate_criterion(
            "AMS",
            "LHR",
            datetime.date(year=2023, month=9, day=6),
        ),
        _generate_criterion(
            "LHR",
            "LAX",
            datetime.date(year=2023, month=9, day=10),
        ),
        _generate_criterion(
            "LAX",
            "AMS",
            datetime.date(year=2023, month=9, day=20),
        ),
    ]


@pytest.fixture()
async def multi_city_response(
    trip_searcher: trips.Trips,
    multi_city_criteria: Sequence[trips_pb2.SearchTripsRequest.Criterion],
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(
        trips_pb2.SearchTripsRequest(
            multi_city=trips_pb2.SearchTripsRequest.MultiCity(
                criteria=multi_city_criteria,
            ),
            passengers=passengers,
        ),
    )


class TestTrips(object):
    def test_one_way_response_contains_results(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(one_way_response.results)

    def test_round_trip_response_contains_power_of_results(
        self,
        round_trip_response: trips_pb2.SearchTripsResponse,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(round_trip_response.results) == len(one_way_response.results) ** 2

    def test_round_trip_response_contains_return_trip(
        self,
        round_trip_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        for trip_result in round_trip_response.results:
            first_outbound_segment = trip_result.trips[0].segments[0]
            last_inbound_segment = trip_result.trips[-1].segments[-1]
            first_leg = first_outbound_segment.legs[0]
            last_leg = last_inbound_segment.legs[-1]
            assert first_leg.origin.ref == last_leg.destination.ref

    def test_multi_city_response_contains_trips(
        self,
        multi_city_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(multi_city_response.results)

    def test_multi_city_response_contains_all_criteria(
        self,
        multi_city_response: trips_pb2.SearchTripsResponse,
        multi_city_criteria: Sequence[trips_pb2.SearchTripsRequest.Criterion],
    ) -> None:
        for trip_result in multi_city_response.results:
            for crit, trip in zip(multi_city_criteria, trip_result.trips, strict=True):
                first_leg = trip.segments[0].legs[0]
                last_leg = trip.segments[-1].legs[-1]
                assert crit.origin_identifier == first_leg.origin.ref
                assert crit.destination_identifier == last_leg.destination.ref

    async def test_unknown_search_response_contains_no_trips(
        self,
        trip_searcher: trips.Trips,
        passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
    ) -> None:
        response = await trip_searcher.find(
            trips_pb2.SearchTripsRequest(
                one_way=trips_pb2.SearchTripsRequest.OneWay(
                    criterion=trips_pb2.SearchTripsRequest.Criterion(
                        origin_identifier="XXX",
                        destination_identifier="YYY",
                        departure_date=protobuf.date_to_protobuf(
                            datetime.date(year=2023, month=9, day=6),
                        ),
                    ),
                ),
                passengers=passengers,
            ),
        )

        assert not len(response.results)


def _generate_criterion(
    origin: str = "ARN",
    destination: str = "LAX",
    departure_date: datetime.date | None = None,
) -> trips_pb2.SearchTripsRequest.Criterion:
    return trips_pb2.SearchTripsRequest.Criterion(
        origin_identifier=origin,
        destination_identifier=destination,
        departure_date=protobuf.date_to_protobuf(
            departure_date or datetime.date(year=2023, month=9, day=6),
        ),
    )
