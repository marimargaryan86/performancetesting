import datetime

import pytest
import pytest_httpx

from snowfall.project.junction.content.service.duffel import conftest, parsers, trips
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2
from snowfall.vendor.duffel import client

_ORIGIN = "SYD"
_DESTINATION = "SIN"
_DEPARTURE_DATE = datetime.date(2023, 2, 23)


@pytest.fixture()
def trips_transformer() -> trips.Transformer:
    return trips.Transformer(parsers.TripParser())


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
        json=await conftest.load_json_fixture(
            "offer_request_response",
            "snowfall.vendor.duffel.client",
        ),
    )

    return await trip_searcher.find_one_way(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
    )


class TestTripSearcher(object):
    def test_one_way_contains_results(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(trip_search_response.results)

    def test_one_way_results_contain_trips(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        for result in trip_search_response.results:
            assert len(result.trips)

    def test_one_way_contains_no_duplicates(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        result_signatures = set()

        for result in trip_search_response.results:
            signature = trips.calculate_result_hash(result)
            assert signature not in result_signatures, "Duplicate result found"
            result_signatures.add(signature)

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


def test_passenger_with_age_is_added_to_request(
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> None:
    offer_request = trips.one_way_to_offer_request(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
    )
    passengers = offer_request.offer_data.passengers
    assert passengers
    assert passengers[0].age == 35


def test_slice_is_added_to_request(
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> None:
    offer_request = trips.one_way_to_offer_request(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
    )
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
