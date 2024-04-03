import datetime
from collections.abc import Iterable
from typing import Any

import aiofiles
import orjson
import pytest
import pytest_httpx

from snowfall.project.junction.content.service.direct_ferries import (
    port,
    routes,
    trips,
)
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import date_pb2, latlng_pb2
from snowfall.vendor.direct_ferries import client

_ORIGIN = latlng_pb2.LatLng(latitude=51.9754793, longitude=4.1255803)
_DESTINATION = latlng_pb2.LatLng(latitude=51.94743, longitude=1.2533101)
_DEPARTURE_DATE = datetime.date(2023, 2, 23)


async def load_json_fixture(
    file_name: str,
    package: str | None = None,
) -> dict[str, Any]:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.json".format(
            file_name=file_name.removesuffix(".json"),
        ),
    )

    async with aiofiles.open(file_path) as file_handle:
        return orjson.loads(await file_handle.read())


@pytest.fixture()
async def h3_port_mapping() -> h3.H3MappingRepository[port.Port]:
    return h3.H3MappingRepository[port.Port](
        mapping=port.load_ports(),
        resolution=8,
    )


@pytest.fixture()
async def trips_transformer(
    h3_port_mapping: h3.H3MappingRepository[port.Port],
) -> trips.Transformer:
    return trips.Transformer(h3_port_mapping=h3_port_mapping)


@pytest.fixture()
async def route_repo() -> routes.RouteRepository:
    return routes.RouteRepository()


@pytest.fixture()
def trip_searcher(
    direct_ferries_client: client.DfHttpClient,
    trips_transformer: trips.Transformer,
    h3_port_mapping: h3.H3MappingRepository[port.Port],
    route_repo: routes.RouteRepository,
) -> trips.Trips:
    return trips.Trips(
        search_client=direct_ferries_client,
        transformer=trips_transformer,
        h3_port_mapping=h3_port_mapping,
        route_repo=route_repo,
    )


class TestTripSearcher:
    def test_one_way_contains_results(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(trip_search_response.results)

    def test_one_way_contains_no_duplicates(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        result_signatures = set()

        for result in trip_search_response.results:
            signature = trips.calculate_result_hash(result)
            assert signature not in result_signatures, "Duplicate result found"
            result_signatures.add(signature)

    def test_trips_have_fare_type(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        for result in trip_search_response.results:
            for trip in result.trips:
                assert trip.fare.type is not None

    async def test_results_are_priced(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_prices(trip_search_response)


@pytest.fixture()
async def trip_search_one_way(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> trips_pb2.SearchTripsRequest:
    httpx_mock.add_response(
        method="POST",
        url="http://localhost/oauth2/token",
        json={
            "expires_in": 100,
            "access_token": "token_mock",
        },
    )

    httpx_mock.add_response(
        method="POST",
        url="http://localhost/api/v1.0/Quotes/get-quotes-request?culture=en-GB",
        json=await load_json_fixture(
            "round_trip_quote_response.json",
        ),
    )
    return trips_pb2.SearchTripsRequest(
        one_way=trips_pb2.SearchTripsRequest.OneWay(
            criterion=trips_pb2.SearchTripsRequest.Criterion(
                origin_coordinates=_ORIGIN,
                destination_coordinates=_DESTINATION,
                departure_date=protobuf.date_to_protobuf(_DEPARTURE_DATE),
            ),
        ),
        passengers=[
            trips_pb2.SearchTripsRequest.Passenger(
                date_of_birth=date_pb2.Date(year=1987, month=5, day=24),
            ),
        ],
    )


@pytest.fixture()
async def trip_search_round_trip(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> trips_pb2.SearchTripsRequest:
    httpx_mock.add_response(
        method="POST",
        url="http://localhost/oauth2/token",
        json={
            "expires_in": 100,
            "access_token": "token_mock",
        },
    )
    httpx_mock.add_response(
        method="POST",
        url="http://localhost/api/v1.0/Quotes/get-quotes-request?culture=en-GB",
        json=await load_json_fixture(
            "round_trip_quote_response.json",
        ),
    )
    return trips_pb2.SearchTripsRequest(
        round_trip=trips_pb2.SearchTripsRequest.RoundTrip(
            criterion=trips_pb2.SearchTripsRequest.Criterion(
                origin_coordinates=_ORIGIN,
                destination_coordinates=_DESTINATION,
                departure_date=protobuf.date_to_protobuf(_DEPARTURE_DATE),
            ),
            return_date=protobuf.date_to_protobuf(_DEPARTURE_DATE),
        ),
        passengers=[
            trips_pb2.SearchTripsRequest.Passenger(
                date_of_birth=date_pb2.Date(year=1987, month=5, day=24),
            ),
        ],
    )


@pytest.fixture()
async def trip_search_response(
    trip_searcher: trips.Trips,
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find_one_way(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
    )


@pytest.fixture()
async def round_trip_search_response(
    trip_searcher: trips.Trips,
    trip_search_round_trip: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find_round_trip(
        trip_search_round_trip.round_trip,
        trip_search_round_trip.passengers,
    )


@pytest.fixture()
def trip_result(
    trip_search_response: trips_pb2.SearchTripsResponse,
) -> trips_pb2.Result:
    return trip_search_response.results[0]


@pytest.fixture()
def round_trip_result(
    round_trip_search_response: trips_pb2.SearchTripsResponse,
) -> trips_pb2.Result:
    return round_trip_search_response.results[0]


@pytest.fixture()
def segments_results(trip_result: trips_pb2.Result) -> list[trips_pb2.Segment]:
    return [segment for trip in trip_result.trips for segment in trip.segments]


@pytest.fixture()
def round_trip_segments_results(
    round_trip_result: trips_pb2.Result,
) -> list[trips_pb2.Segment]:
    return [segment for trip in round_trip_result.trips for segment in trip.segments]


class TestSegmentModel:
    def test_locations(self, segments_results: Iterable[trips_pb2.Segment]) -> None:
        for segment in segments_results:
            self._assert_location(segment.origin)
            self._assert_location(segment.destination)

    def test_segment_has_arrival_and_departure(
        self,
        segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in segments_results:
            assert segment.departure_at.year
            assert segment.arrival_at.year

    def test_segment_has_vehicles(
        self,
        segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in segments_results:
            self._assert_vehicle(segment.vehicle)

    def _assert_location(self, location: trips_pb2.Location) -> None:
        assert location.ref, "Locations should have a ref"
        assert location.name, "Locations should have a name"
        assert location.coordinates.longitude, "Locations should have longitude"
        assert location.coordinates.latitude, "Locations should have latitude"

    def _assert_vehicle(self, vehicle: trips_pb2.Segment.Vehicle) -> None:
        assert vehicle.name, "Vehicles should have a name"


class TestRoundTripSegmentModel:
    def test_locations(
        self,
        round_trip_segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in round_trip_segments_results:
            self._assert_location(segment.origin)
            self._assert_location(segment.destination)

    def test_segment_has_arrival_and_departure(
        self,
        round_trip_segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in round_trip_segments_results:
            assert segment.departure_at.year
            assert segment.arrival_at.year

    def test_segment_has_vehicles(
        self,
        round_trip_segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in round_trip_segments_results:
            self._assert_vehicle(segment.vehicle)

    def _assert_location(self, location: trips_pb2.Location) -> None:
        assert location.ref, "Locations should have a ref"
        assert location.name, "Locations should have a name"
        assert location.coordinates.longitude, "Locations should have longitude"
        assert location.coordinates.latitude, "Locations should have latitude"

    def _assert_vehicle(self, vehicle: trips_pb2.Segment.Vehicle) -> None:
        assert vehicle.name, "Vehicles should have a name"


def _assert_result_prices(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        assert (
            trip_result.base_amount.currency_code
        ), "Results should have a base amount"
        assert (
            trip_result.total_amount.currency_code
        ), "Results should have a total amount"
