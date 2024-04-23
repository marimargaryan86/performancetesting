import datetime
import uuid
import zoneinfo

from snowfall.project.junction.go.v1 import models_pb2 as go_models
from snowfall.project.junction.rocket import fixtures
from snowfall.project.junction.rocket.service.providers.silverrail import (
    adapter,
    constant,
    criteria,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import latlng_pb2


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False

    return True


async def test_successful(  # noqa: WPS218
    silverrail_search_result_generator: adapter.SilverrailOffersAdapter,
) -> None:
    now = datetime.datetime.now(tz=datetime.UTC)
    search_task = criteria.Criteria(
        search_id=fixtures.RAIL_SEARCH_ID,
        origin="FRLYS",
        destination="FRXYD",
        outbound_departure_after=now,
        outbound_departure_before=now + datetime.timedelta(days=2),
        passenger_dobs=[
            (now - datetime.timedelta(days=365 * 30)).date(),
        ],
    )
    results = [
        result
        async for result in silverrail_search_result_generator.gather_search_results(
            search_task,
        )
    ]

    assert len(results) == 6

    result = results[0]
    assert is_uuid(result.id)
    assert result.search_id == fixtures.RAIL_SEARCH_ID
    assert result.provider_id == str(constant.PROVIDER_ID)
    assert protobuf.protobuf_to_datetime(result.expires_at) > datetime.datetime.now(
        tz=datetime.UTC,
    )
    assert len(result.offers) == 3
    assert len(result.result_details) == 1

    offer = result.offers[0]
    assert is_uuid(offer.id)
    assert offer.price.units == 31
    assert offer.price.currency_code == "EUR"
    assert len(offer.rail.cabin_class) == 1
    cabin_detail = offer.rail.cabin_class[0]
    assert cabin_detail.cabin_class.type == go_models.CabinClass.TYPE_ECONOMY
    assert cabin_detail.result_id == result.id
    assert len(offer.price_breakdown) == 1
    price_breakdown = offer.price_breakdown[0]
    assert price_breakdown.price.units == 31
    assert price_breakdown.price.currency_code == "EUR"
    assert (
        price_breakdown.breakdown_type
        == models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    result_detail = result.result_details[0]
    assert is_uuid(result_detail.id)
    rail = result_detail.rail
    assert rail.segment_sequence == 1
    assert rail.outbound_segment
    expected_departure = datetime.datetime(
        year=2024,
        month=6,
        day=29,
        hour=10,
        tzinfo=zoneinfo.ZoneInfo("Europe/Paris"),
    )
    expected_arrival = datetime.datetime(
        year=2024,
        month=6,
        day=29,
        hour=11,
        minute=56,
        tzinfo=zoneinfo.ZoneInfo("CET"),
    )
    assert protobuf.protobuf_to_datetime(rail.departure_date) == expected_departure
    assert protobuf.protobuf_to_datetime(rail.arrival_date) == expected_arrival
    assert rail.origin.ref == "FRLYS"
    assert rail.origin.name == "Paris Gare De Lyon"
    assert rail.origin.time_zone == "Europe/Paris"
    assert rail.origin.coordinates == latlng_pb2.LatLng(
        latitude=48.8448404,
        longitude=2.3744416,
    )
    assert rail.destination.ref == "FRXYD"
    assert rail.destination.name == "Lyon Part Dieu"
    assert rail.destination.time_zone == "CET"
    assert rail.destination.coordinates == latlng_pb2.LatLng(
        latitude=45.7611339,
        longitude=4.8527867,
    )
