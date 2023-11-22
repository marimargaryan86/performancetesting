import datetime
import zoneinfo
from collections.abc import Mapping, Sequence

import pytest

from snowfall.project.junction.content.service.mock import client
from snowfall.project.junction.provider.v2alpha import trips_pb2


def _generate_mock_trip(
    duration: datetime.timedelta,
) -> client.Trip:
    departure_at = datetime.datetime(
        year=2023,
        month=9,
        day=13,
        hour=8,
        tzinfo=datetime.UTC,
    )
    arrival_at = departure_at + duration

    return client.Trip(
        segments=[
            client.Segment(
                origin=_generate_stop("foo"),
                destination=_generate_stop("bar"),
                departure_at=departure_at,
                arrival_at=arrival_at,
                marketed_by=client.Company(
                    flight_number="123",
                    name="Foo",
                    code="foo",
                ),
                operated_by=client.Company(
                    flight_number="234",
                    name="Bar",
                    code="bar",
                ),
            ),
        ],
    )


def _generate_stop(ref: str) -> client.Stop:
    return client.Stop(
        identifier=ref,
        name="",
        country_code="SE",
        rad_latitude=0,
        rad_longitude=0,
        latitude=0,
        longitude=0,
        timezone=zoneinfo.ZoneInfo("UTC"),
    )


class TestClient(object):
    def test_one_way_contains_results(
        self,
        mock_client: client.MockClient,
        one_way_request: trips_pb2.SearchTripsRequest,
    ) -> None:
        results = mock_client.find_one_way(one_way_request.one_way)
        assert len(results)

    def test_round_trip_contains_power_of_results(
        self,
        mock_client: client.MockClient,
        one_way_request: trips_pb2.SearchTripsRequest,
        roundtrip_request: trips_pb2.SearchTripsRequest,
    ) -> None:
        one_way_results = mock_client.find_one_way(one_way_request.one_way)
        roundtrip_results = mock_client.find_round_trip(roundtrip_request.round_trip)
        assert len(roundtrip_results) == len(one_way_results) ** 2


class TestFarePrices(object):
    @pytest.mark.parametrize(
        ("fake_trips", "expected"),
        [
            (
                [_generate_mock_trip(duration=datetime.timedelta(hours=2, minutes=40))],
                {
                    "Basic": (140, 150),
                    "Premium": (195, 210),
                    "Business": (350, 400),
                },
            ),
            (
                [_generate_mock_trip(duration=datetime.timedelta(hours=9, minutes=5))],
                {
                    "Basic": (1500, 1700),
                    "Premium": (2300, 2400),
                    "Business": (4300, 4500),
                },
            ),
        ],
    )
    def test_prices_in_expected_range(
        self,
        fake_trips: Sequence[client.Trip],
        expected: Mapping[str, tuple[int, int]],
    ) -> None:
        for fare in client.FakeFareGenerator(fake_trips).generate():
            lower_limit = expected[fare.brand_name][0]
            upper_limit = expected[fare.brand_name][1]
            assert (
                lower_limit <= float(str(fare.price)) <= upper_limit
            ), "Brand {0} price {1} not within range {2}-{3}".format(
                fare.brand_name,
                str(fare.price),
                lower_limit,
                upper_limit,
            )
