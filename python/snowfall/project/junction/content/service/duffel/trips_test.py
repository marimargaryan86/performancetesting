import datetime
from collections.abc import AsyncIterator, Iterable
from typing import Any

import aiofiles
import httpx
import orjson
import pytest
import pytest_httpx

from snowfall.project.junction.content.service.duffel import trips
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem
from snowfall.stdlib.v1 import date_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.models import offer_slice

_ORIGIN = "SYD"
_DESTINATION = "SIN"
_DEPARTURE_DATE = datetime.date(2023, 2, 23)


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
def duffel_client(http_client: httpx.AsyncClient) -> client.DuffelClient:
    return client.DuffelClient(
        api_base_url="http://localhost",
        api_key="foo",
        version="bar",
        http_client=http_client,
    )


@pytest.fixture()
def trips_transformer() -> trips.Transformer:
    return trips.Transformer()


@pytest.fixture()
def trip_searcher(
    duffel_client: client.DuffelClient,
    trips_transformer: trips.Transformer,
) -> trips.Trips:
    return trips.Trips(
        search_client=duffel_client,
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
    httpx_mock.add_response(
        json=await _load_json_fixture(
            "offer_request_response",
            "snowfall.vendor.duffel.client",
        ),
    )

    return await trip_searcher.find(trip_search_one_way)


class TestTripSearcher(object):
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
async def segment_with_stops(
    trips_transformer: trips.Transformer,
) -> trips_pb2.Segment:
    fixture = await _load_json_fixture("segment_with_stops")
    segment_model = offer_slice.OfferSliceSegment(**fixture)

    return trips_transformer.segment_to_proto(segment_model)


class TestSegmentModel(object):
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

    def test_segment_has_stops(
        self,
        segment_with_stops: trips_pb2.Segment,
    ) -> None:
        assert segment_with_stops.stops

    def test_stop_locations(
        self,
        segment_with_stops: trips_pb2.Segment,
    ) -> None:
        for stop in segment_with_stops.stops:
            self._assert_location(stop.location)

    def test_stop_locations_have_arrival_and_departure(
        self,
        segment_with_stops: trips_pb2.Segment,
    ) -> None:
        for stop in segment_with_stops.stops:
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


def test_passenger_with_age_is_added_to_request(
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> None:
    offer_request = trips.trip_search_to_offer_request(trip_search_one_way)
    passengers = offer_request.offer_data.passengers
    assert passengers
    assert passengers[0].age == 35


def test_slice_is_added_to_request(
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> None:
    offer_request = trips.trip_search_to_offer_request(trip_search_one_way)
    slices = offer_request.offer_data.slices
    assert slices
    first_slice = slices[0]
    assert first_slice.origin == _ORIGIN
    assert first_slice.destination == _DESTINATION
    assert first_slice.departure_date == _DEPARTURE_DATE


def _assert_result_prices(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        assert (
            trip_result.base_amount.currency_code
        ), "Results should have a base amount"
        assert trip_result.tax_amount.currency_code, "Results should have a tax amount"
        assert (
            trip_result.total_amount.currency_code
        ), "Results should have a total amount"
