import datetime
from collections.abc import Sequence

import pytest

from snowfall.project.junction.content.service.mock import client, trips
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib.format import protobuf


@pytest.fixture()
def transformer() -> trips.Transformer:
    return trips.Transformer()


@pytest.fixture()
def trip_searcher(
    mock_client: client.MockClient,
    transformer: trips.Transformer,
) -> trips.Trips:
    return trips.Trips(search_client=mock_client, transformer=transformer)


@pytest.fixture()
async def one_way_response(
    trip_searcher: trips.Trips,
    one_way_request: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(one_way_request)


@pytest.fixture()
async def round_trip_response(
    trip_searcher: trips.Trips,
    roundtrip_request: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(roundtrip_request)


@pytest.fixture()
async def multi_city_response(
    trip_searcher: trips.Trips,
    multi_city_request: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find(multi_city_request)


class TestTrips(object):
    def test_one_way_contains_results(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(one_way_response.results)

    def test_one_way_contains_prices(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_prices(one_way_response)

    def test_one_way_contains_fares(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_trip_fares(one_way_response)

    def test_one_way_contains_companies(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_company_info(one_way_response)

    def test_one_way_contains_vehicles(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_vehicle_info(one_way_response)

    def test_one_way_contains_passenger_seating(
        self,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_passenger_seating(one_way_response)

    def test_round_trip_contains_power_of_results(
        self,
        round_trip_response: trips_pb2.SearchTripsResponse,
        one_way_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(round_trip_response.results) > len(one_way_response.results)

    def test_round_trip_contains_return_trip(
        self,
        round_trip_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        for trip_result in round_trip_response.results:
            first_outbound_segment = trip_result.trips[0].segments[0]
            last_inbound_segment = trip_result.trips[-1].segments[-1]
            assert (
                first_outbound_segment.origin.ref
                == last_inbound_segment.destination.ref
            )

    def test_round_trip_contains_prices(
        self,
        round_trip_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        _assert_result_prices(round_trip_response)

    def test_multi_city_contains_trips(
        self,
        multi_city_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(multi_city_response.results)

    def test_multi_city_contains_all_criteria(
        self,
        multi_city_response: trips_pb2.SearchTripsResponse,
        multi_city_criteria: Sequence[trips_pb2.SearchTripsRequest.Criterion],
    ) -> None:
        for trip_result in multi_city_response.results:
            for crit, trip in zip(multi_city_criteria, trip_result.trips, strict=True):
                assert crit.origin_identifier == trip.segments[0].origin.ref
                assert crit.destination_identifier == trip.segments[-1].destination.ref

    async def test_unknown_search_contains_no_trips(
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


def _assert_result_prices(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        assert (
            trip_result.base_amount.currency_code
        ), "Results should have a base amount"
        assert trip_result.tax_amount.currency_code, "Results should have a tax amount"
        assert (
            trip_result.total_amount.currency_code
        ), "Results should have a total amount"


def _assert_result_trip_fares(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        for trip in trip_result.trips:
            assert trip.fare.type, "Trips should have a fare type"
            assert trip.fare.marketing_name, "Trips should have a fare marketing name"


def _assert_result_company_info(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        for trip in trip_result.trips:
            for segment in trip.segments:
                _assert_segment_company(segment.marketed_by)
                _assert_segment_company(segment.operated_by)


def _assert_segment_company(company: trips_pb2.Segment.Company) -> None:
    assert company.route_number, "Segment company should have a route number"
    assert company.code, "Segment company should have a code"
    assert company.name, "Segment company should have a name"


def _assert_result_vehicle_info(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        for trip in trip_result.trips:
            for segment in trip.segments:
                assert segment.vehicle.code, "Segment vehicle should have a code"
                assert segment.vehicle.name, "Segment vehicle should have a name"


def _assert_result_passenger_seating(response: trips_pb2.SearchTripsResponse) -> None:
    for trip_result in response.results:
        for trip in trip_result.trips:
            for segment in trip.segments:
                assert segment.passengers, "Segments must have passengers"

                for passenger in segment.passengers:
                    _assert_passenger_seating(passenger)


def _assert_passenger_seating(passenger: trips_pb2.Segment.Passenger) -> None:
    assert passenger.seating.type, "Passenger seating should have a type"
    assert passenger.seating.marketing_name, "Passenger seating should have a name"
