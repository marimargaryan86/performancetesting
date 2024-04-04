import datetime
from collections.abc import AsyncIterator, Iterable
from typing import Any

import aiofiles
import httpx
import orjson
import pytest
import pytest_httpx
from motor import motor_asyncio

from snowfall.project.junction.content.service.ask2go import trips
from snowfall.project.junction.provider import airports, cabin_classes
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import date_pb2
from snowfall.vendor.ask2go import client
from snowfall.vendor.ask2go.adapter import Adapter
from snowfall.vendor.ask2go.models import offers

_ORIGIN = "SYD"
_DESTINATION = "SIN"
_DEPARTURE_DATE = datetime.date(2023, 2, 23)


@pytest.fixture()
async def cabin_class_repo(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> cabin_classes.CabinMappingRepository:
    return cabin_classes.CabinMappingRepository(
        collection=mongo_client.test.provider_cabin_mapping,
    )


async def _load_json_fixture(
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
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def search_client(http_client: httpx.AsyncClient) -> client.Ask2GoClient:
    return client.Ask2GoClient(
        api_base_url="http://localhost",
        api_booking_base_url="http://localhost",
        http_client=http_client,
    )


@pytest.fixture()
def trips_transformer(
    cabin_class_repo: cabin_classes.CabinMappingRepository,
) -> trips.Transformer:
    airport_repo = airports.AirportRepository(
        filesystem.PkgLoader("snowfall.data").load("airports.json"),
    )
    return trips.Transformer(airport_repo, cabin_class_repo)


@pytest.fixture()
def trip_searcher(
    search_client: client.Ask2GoClient,
    trips_transformer: trips.Transformer,
) -> trips.Trips:
    return trips.Trips(
        adapter=Adapter(
            ask2go_client=search_client,
            poll_retries_limit=1,
            wait_time_between_polling=0,
        ),
        transformer=trips_transformer,
    )


@pytest.fixture()
def trip_search_one_way() -> trips_pb2.SearchTripsRequest:
    return trips_pb2.SearchTripsRequest(
        one_way=trips_pb2.SearchTripsRequest.OneWay(
            criterion=trips_pb2.SearchTripsRequest.Criterion(
                origin_identifier=_ORIGIN,
                destination_identifier=_DESTINATION,
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
async def trip_search_response(
    httpx_mock: pytest_httpx.HTTPXMock,
    trip_searcher: trips.Trips,
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    httpx_mock.add_response(json={"id": 1, "transaction_id": 1})
    httpx_mock.add_response(
        json=await _load_json_fixture(
            "offer_request_response",
            "snowfall.vendor.ask2go.client",
        ),
    )

    return await trip_searcher.find_one_way(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
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
                assert trip.fare.type

    def test_trips_have_fare_marketing_name(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        for result in trip_search_response.results:
            for trip in result.trips:
                assert trip.fare.marketing_name

    async def test_results_are_priced(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_prices(trip_search_response)


@pytest.fixture()
def trip_result(
    trip_search_response: trips_pb2.SearchTripsResponse,
) -> trips_pb2.Result:
    return trip_search_response.results[0]


@pytest.fixture()
def segments_results(trip_result: trips_pb2.Result) -> list[trips_pb2.Segment]:
    return [segment for trip in trip_result.trips for segment in trip.segments]


@pytest.fixture()
async def segment(
    trips_transformer: trips.Transformer,
) -> trips_pb2.Segment:
    fixture = await _load_json_fixture("segment")
    segment_model = offers.TripSegment(**fixture)

    return trips_transformer.segment_to_proto(segment_model)


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

    def test_segment_has_companies(
        self,
        segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in segments_results:
            self._assert_company(segment.marketed_by)
            self._assert_company(segment.operated_by)

    def test_segment_has_vehicles(
        self,
        segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in segments_results:
            self._assert_vehicle(segment.vehicle)

    def test_segment_has_passenger_seating(
        self,
        segments_results: Iterable[trips_pb2.Segment],
    ) -> None:
        for segment in segments_results:
            assert segment.passengers, "Segments must have passengers"

            for passenger in segment.passengers:
                self._assert_passenger_seating(passenger)

    def test_stop_locations(
        self,
        segment: trips_pb2.Segment,
    ) -> None:
        for stop in segment.stops:
            self._assert_location(stop.location)

    def test_stop_locations_have_arrival_and_departure(
        self,
        segment: trips_pb2.Segment,
    ) -> None:
        for stop in segment.stops:
            assert stop.arrival_at.year
            assert stop.departure_at.year

    def _assert_location(self, location: trips_pb2.Location) -> None:
        assert location.ref, "Locations should have a ref"
        assert location.name, "Locations should have a name"
        assert location.coordinates.longitude, "Locations should have longitude"
        assert location.coordinates.latitude, "Locations should have latitude"

    def _assert_company(self, company: trips_pb2.Segment.Company) -> None:
        assert company.code, "Companies should have a code"
        assert company.name, "Companies should have a name"
        assert company.route_number, "Companies should have a route number"

    def _assert_vehicle(self, vehicle: trips_pb2.Segment.Vehicle) -> None:
        assert vehicle.code, "Vehicles should have a code"
        assert vehicle.name, "Vehicles should have a name"

    def _assert_passenger_seating(self, passenger: trips_pb2.Segment.Passenger) -> None:
        assert passenger.seating.type, "Passenger seating should have a type"
        assert passenger.seating.marketing_name, "Passenger seating should have a name"


def _assert_result_prices(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        assert (
            trip_result.base_amount.currency_code
        ), "Results should have a base amount"
        assert trip_result.tax_amount.currency_code, "Results should have a tax amount"
        assert (
            trip_result.total_amount.currency_code
        ), "Results should have a total amount"
