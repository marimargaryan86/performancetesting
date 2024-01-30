import datetime
from collections.abc import Iterable
from types import MappingProxyType

import pytest

from snowfall.project.junction.content.service.benerail import (
    adapter,
    train_stations,
    trips,
)
from snowfall.project.junction.provider import cabin_classes
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.stdlib import h3
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import date_pb2, latlng_pb2
from snowfall.vendor.benerail import client

_ORIGIN = MappingProxyType({"latitude": 50.8601446, "longitude": 4.3614901})
_DESTINATION = MappingProxyType({"latitude": 50.8356748, "longitude": 4.3362419})
_DEPARTURE_DATE = datetime.date(2023, 2, 23)


@pytest.fixture()
def trips_transformer(
    benerail_client: client.BenerailClient,
    provider_cabin_class_mapping: cabin_classes.CabinMappingRepository,
    train_station_repository: train_stations.TrainStationRepository,
) -> trips.Transformer:
    return trips.Transformer(
        benerail_client=benerail_client,
        provider_cabin_class_mapping=provider_cabin_class_mapping,
        train_station_repository=train_station_repository,
    )


@pytest.fixture()
def trip_searcher(
    benerail_client: client.BenerailClient,
    benerail_adapter: adapter.BenerailAdapter,
    trips_transformer: trips.Transformer,
    station_mapping: h3.H3MappingRepository[train_stations.TrainStation],
    train_station_repository: train_stations.TrainStationRepository,
) -> trips.Trips:
    return trips.Trips(
        benerail_adapter=benerail_adapter,
        transformer=trips_transformer,
        station_mapping=station_mapping,
        train_station_repository=train_station_repository,
        should_retrieve_offers=False,
    )


@pytest.fixture()
def trip_search_one_way() -> trips_pb2.SearchTripsRequest:
    return trips_pb2.SearchTripsRequest(
        one_way=trips_pb2.SearchTripsRequest.OneWay(
            criterion=trips_pb2.SearchTripsRequest.Criterion(
                origin_coordinates=latlng_pb2.LatLng(
                    latitude=_ORIGIN["latitude"],
                    longitude=_ORIGIN["longitude"],
                ),
                destination_coordinates=latlng_pb2.LatLng(
                    latitude=_DESTINATION["latitude"],
                    longitude=_DESTINATION["longitude"],
                ),
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
    trip_searcher: trips.Trips,
    trip_search_one_way: trips_pb2.SearchTripsRequest,
) -> trips_pb2.SearchTripsResponse:
    return await trip_searcher.find_one_way(
        trip_search_one_way.one_way,
        trip_search_one_way.passengers,
    )


@pytest.mark.usefixtures("train_rcode_response", "cabin_class_rcode_response")
class TestTripSearcher(object):
    def test_one_way_contains_results(
        self,
        trip_search_response: trips_pb2.SearchTripsResponse,
    ) -> None:
        assert len(trip_search_response.results)

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
        self._assert_result_prices(trip_search_response)

    def _assert_result_prices(self, response: trips_pb2.SearchTripsResponse) -> None:
        for trip_result in response.results:
            assert (
                trip_result.base_amount.currency_code
            ), "Results should have a base amount"
            assert (
                trip_result.tax_amount.currency_code
            ), "Results should have a tax amount"
            assert (
                trip_result.total_amount.currency_code
            ), "Results should have a total amount"


@pytest.fixture()
def trip_result(
    trip_search_response: trips_pb2.SearchTripsResponse,
) -> trips_pb2.Result:
    return trip_search_response.results[0]


@pytest.fixture()
def segments_results(trip_result: trips_pb2.Result) -> list[trips_pb2.Segment]:
    return [segment for trip in trip_result.trips for segment in trip.segments]


@pytest.mark.usefixtures("train_rcode_response", "cabin_class_rcode_response")
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

    def _assert_location(self, location: trips_pb2.Location) -> None:
        assert location.ref, "Locations should have a ref"
        assert location.name, "Locations should have a name"
        assert location.coordinates.longitude, "Locations should have longitude"
        assert location.coordinates.latitude, "Locations should have latitude"

    def _assert_vehicle(self, vehicle: trips_pb2.Segment.Vehicle) -> None:
        assert vehicle.code, "Vehicles should have a code"
        assert vehicle.name, "Vehicles should have a name"

    def _assert_passenger_seating(self, passenger: trips_pb2.Segment.Passenger) -> None:
        # assert passenger.seating.type, "Passenger seating should have a type"
        assert passenger.seating.marketing_name, "Passenger seating should have a name"
