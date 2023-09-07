import datetime
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
async def generic_response(
    trip_searcher: trips.Trips,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(
        trips_pb2.SearchTripsRequest(
            criterion=[
                trips_pb2.Criterion(
                    origin_identifier="ARN",
                    destination_identifier="LHR",
                    departure_date=protobuf.date_to_protobuf(
                        datetime.date(year=2023, month=9, day=6),
                    ),
                ),
            ],
            passengers=[
                trips_pb2.Passenger(
                    date_of_birth=protobuf.date_to_protobuf(
                        datetime.date(year=1987, month=5, day=24),
                    ),
                ),
            ],
        ),
    )


class TestTrips(object):
    def test_result_contains_trips(
        self,
        generic_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(generic_response.trips)

    async def test_unknown_search_result_contains_no_trips(
        self,
        trip_searcher: trips.Trips,
    ) -> None:
        response = await trip_searcher.find(
            trips_pb2.SearchTripsRequest(
                criterion=[
                    trips_pb2.Criterion(
                        origin_identifier="XXX",
                        destination_identifier="YYY",
                        departure_date=protobuf.date_to_protobuf(
                            datetime.date(year=2023, month=9, day=6),
                        ),
                    ),
                ],
                passengers=[
                    trips_pb2.Passenger(
                        date_of_birth=protobuf.date_to_protobuf(
                            datetime.date(year=1987, month=5, day=24),
                        ),
                    ),
                ],
            ),
        )

        assert not len(response.trips)
