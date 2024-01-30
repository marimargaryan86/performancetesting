import datetime
import math
import zoneinfo

import pytest

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.project.junction.service.providers.ask2go import (
    conftest,
    search,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.v1 import amqp_pb2
from snowfall.stdlib import money
from snowfall.stdlib.format import protobuf
from snowfall.vendor.ask2go.adapter import Adapter

_ARN_LHR = amqp_pb2.SearchCriteriaTask(
    segments=[
        models_pb2.Segment(
            id="segment_id",
            legs=[
                models_pb2.Leg(
                    id="leg_id",
                    origin=models_pb2.Point(
                        time_zone="Europe/Stockholm",
                    ),
                    destination=models_pb2.Point(
                        time_zone="Europe/London",
                    ),
                    departure_at=protobuf.datetime_to_protobuf(
                        datetime.datetime(
                            2023,
                            2,
                            14,
                            15,
                            20,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        datetime.datetime(
                            2023,
                            2,
                            14,
                            17,
                            0,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/London"),
                        ),
                    ),
                ),
            ],
        ),
    ],
    criteria=amqp_pb2.Criteria(
        origin_iata="ARN",
        destination_iata="LHR",
        outbound_departure=protobuf.datetime_to_protobuf_datetime(
            datetime.datetime(
                year=2023,
                month=2,
                day=21,
                hour=15,
                minute=20,
                second=0,
                tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
            ),
        ),
        cabin_class="Any",
        adults=1,
    ),
)


async def test_search_result_data(  # noqa: WPS218
    search_adapter: Adapter,
    offer_transformer: transformer.OfferTransformer,
    magic_mocker: conftest.MagicMocker,
) -> None:
    with magic_mocker.with_fixture_path("branded_search"):
        offer_groups = [
            group
            async for group in offer_transformer.to_offer_groups(
                search_adapter.gather_search_results(
                    search.search_criteria_generator(_ARN_LHR),
                ),
            )
        ]

    assert len(offer_groups) == 10

    offer_group = offer_groups[0]

    segment = offer_group.segments[0]
    _assert_offer(offer_group.offers[0], segment.id)
    assert segment.segment_id == ""
    assert segment.operator == "SK"
    assert segment.vendor == "SK"
    assert segment.terminal == "5"
    assert segment.vehicle.equipment == "32N"
    assert segment.vehicle.number == "527"
    assert segment.type == models_pb2.Schedule.TYPE_AIR
    leg = segment.legs[0]
    assert leg.origin.ref == "ARN"
    assert leg.origin.name == "Stockholm-Arlanda Airport"
    assert leg.origin.time_zone == "Europe/Stockholm"
    assert math.isclose(leg.origin.coordinates.latitude, 59.650831)
    assert math.isclose(leg.origin.coordinates.longitude, 17.92119)
    assert leg.destination.ref == "LHR"
    assert leg.destination.name == "Heathrow Airport"
    assert leg.destination.time_zone == "Europe/London"
    assert math.isclose(leg.destination.coordinates.latitude, 51.470311)
    assert math.isclose(leg.destination.coordinates.longitude, -0.458118)
    expected_leg = _ARN_LHR.segments[0].legs[0]
    assert leg.departure_at == expected_leg.departure_at
    assert leg.arrival_at == expected_leg.arrival_at


def _assert_offer(  # noqa: WPS218
    offer: offers_pb2.Offer,
    expected_segment_id: str,
) -> None:
    segment_details = offer.segment_details[0]
    assert segment_details.offer_segment_id == expected_segment_id
    assert segment_details.cabin_class.marketing_name == "Economy"
    assert (
        segment_details.cabin_class.type == models_pb2.CabinClass.Type.TYPE_UNSPECIFIED
    )
    assert (
        segment_details.amenities.beverage.availability
        == offers_pb2.SegmentAmenity.TYPE_AVAILABLE
    )
    assert (
        segment_details.amenities.power.availability
        == offers_pb2.SegmentAmenity.TYPE_INCLUDED
    )
    price = money.from_protobuf(offer.price)
    assert str(price) == "55.54"
    assert price.currency.code == "EUR"
    assert offer.brand_name == "LOWEST FARE AVAILABLE"

    _assert_price_breakdown(offer)


def _assert_price_breakdown(offer: offers_pb2.Offer) -> None:  # noqa: WPS218
    base_fare = offer.price_breakdown[0]
    base_fare_price = money.from_protobuf(base_fare.price)
    assert str(base_fare_price) == "13.00"
    assert base_fare_price.currency.code == "EUR"
    assert (
        base_fare.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    tax = offer.price_breakdown[1]
    tax_price = money.from_protobuf(tax.price)
    assert str(tax_price) == "42.54"
    assert tax_price.currency.code == "EUR"
    assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX


@pytest.mark.parametrize(
    ("departure_time", "expected"),
    [
        (
            datetime.time(hour=3, minute=45),
            (datetime.time(hour=0), datetime.time(hour=6)),
        ),
        (
            datetime.time(hour=0, minute=0),
            (datetime.time(hour=0), datetime.time(hour=6)),
        ),
        (
            datetime.time(hour=6, minute=0),
            (datetime.time(hour=6), datetime.time(hour=12)),
        ),
        (
            datetime.time(hour=17, minute=56),
            (datetime.time(hour=12), datetime.time(hour=18)),
        ),
        (
            datetime.time(hour=23, minute=45),
            (datetime.time(hour=18), datetime.time(hour=00)),
        ),
    ],
)
def test_time_to_window(
    departure_time: datetime.time,
    expected: tuple[datetime.time, datetime.time],
) -> None:
    assert search.time_to_window(departure_time) == expected
