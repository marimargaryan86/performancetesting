import datetime
from collections.abc import Sequence
from typing import Any, cast

import pytest

from snowfall.project.junction.content.service.mock import client
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import date_pb2


@pytest.fixture()
def stop_repository() -> client.StopRepository:
    return client.StopRepository(
        stops=cast(
            list[dict[str, Any]],
            filesystem.PkgLoader(__name__).load("stops.json"),
        ),
    )


@pytest.fixture()
def route_repository(stop_repository: client.StopRepository) -> client.RouteRepository:
    return client.RouteRepository(
        stop_repository=stop_repository,
        routes=cast(
            list[list[str]],
            filesystem.PkgLoader(__name__).load("routes.json"),
        ),
    )


@pytest.fixture()
def mock_client(route_repository: client.RouteRepository) -> client.MockClient:
    return client.MockClient(route_repository=route_repository)


@pytest.fixture()
def passengers() -> list[trips_pb2.SearchTripsRequest.Passenger]:
    return [
        trips_pb2.SearchTripsRequest.Passenger(
            date_of_birth=date_pb2.Date(year=1990, month=10, day=25),
        ),
    ]


@pytest.fixture()
def one_way_request(
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsRequest:
    return trips_pb2.SearchTripsRequest(
        one_way=trips_pb2.SearchTripsRequest.OneWay(
            criterion=_generate_criterion(),
        ),
        passengers=passengers,
    )


@pytest.fixture()
def roundtrip_request(
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsRequest:
    return trips_pb2.SearchTripsRequest(
        round_trip=trips_pb2.SearchTripsRequest.RoundTrip(
            criterion=_generate_criterion(),
            return_date=protobuf.date_to_protobuf(
                datetime.date(year=2023, month=9, day=10),
            ),
        ),
        passengers=passengers,
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
def multi_city_request(
    multi_city_criteria: Sequence[trips_pb2.SearchTripsRequest.Criterion],
    passengers: Sequence[trips_pb2.SearchTripsRequest.Passenger],
) -> trips_pb2.SearchTripsRequest:
    return trips_pb2.SearchTripsRequest(
        multi_city=trips_pb2.SearchTripsRequest.MultiCity(
            criteria=multi_city_criteria,
        ),
        passengers=passengers,
    )


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
