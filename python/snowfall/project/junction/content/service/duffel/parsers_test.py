from collections.abc import Iterable, Sequence

import pytest
import pytest_httpx

from snowfall.project.junction.content.service.duffel import conftest, parsers
from snowfall.project.junction.provider.v2alpha import trips_pb2
from snowfall.vendor.duffel import client
from snowfall.vendor.duffel.builders import offer_request
from snowfall.vendor.duffel.models import offer_slice


@pytest.fixture()
def trip_parser() -> parsers.TripParser:
    return parsers.TripParser()


@pytest.fixture()
async def trip_results(
    httpx_mock: pytest_httpx.HTTPXMock,
    duffel_client: client.DuffelClient,
    trip_parser: parsers.TripParser,
) -> list[trips_pb2.Trip]:
    httpx_mock.add_response(
        json=await conftest.load_json_fixture(
            "offer_request_response",
            "snowfall.vendor.duffel.client",
        ),
    )
    result = await duffel_client.create_offer_request(
        offer_request_data=offer_request.OfferRequestData(
            offer_data=offer_request.OfferRequestDataList(
                passengers=[],
                slices=[],
            ),
        ),
    )

    return [
        trip_parser.trip_to_proto(trip)
        for offer in result.offers
        for trip in offer.slices
    ]


@pytest.fixture()
def trip_result(
    trip_results: Sequence[trips_pb2.Trip],
) -> trips_pb2.Trip:
    return trip_results[0]


class TestTripModel(object):
    def test_trips_have_fare_type(
        self,
        trip_results: Sequence[trips_pb2.Trip],
    ) -> None:
        for trip in trip_results:
            assert trip.fare.type

    def test_trips_have_fare_marketing_name(
        self,
        trip_results: Sequence[trips_pb2.Trip],
    ) -> None:
        for trip in trip_results:
            assert trip.fare.marketing_name


@pytest.fixture()
def segments_results(trip_result: trips_pb2.Trip) -> list[trips_pb2.Segment]:
    return list(trip_result.segments)


@pytest.fixture()
async def segment_with_stops(
    trip_parser: parsers.TripParser,
) -> trips_pb2.Segment:
    fixture = await conftest.load_json_fixture("segment_with_stops")
    segment_model = offer_slice.OfferSliceSegment(**fixture)

    return trip_parser.segment_to_proto(segment_model)


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

    def _assert_vehicle(self, vehicle: trips_pb2.Segment.Vehicle) -> None:
        assert vehicle.code, "Vehicles should have a code"
        assert vehicle.name, "Vehicles should have a name"

    def _assert_passenger_seating(self, passenger: trips_pb2.Segment.Passenger) -> None:
        assert passenger.seating.type, "Passenger seating should have a type"
        assert passenger.seating.marketing_name, "Passenger seating should have a name"
