import datetime
import math
import zoneinfo
from typing import Any, Mapping

import pytest
import pytest_httpx

from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ask2go import (
    adapter,
    conftest,
    transformer,
)
from snowfall.project.junction.service.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2

_OFFER_URL = "https://test_url/api/search/{id}/{transaction}/{page}"
_PRICE_URL = (
    "https://test_url/api/Itinerary/{id}/{offer}/Price?"
    + "transactionId={transaction_id}&brandId={brand_id}"
)
_VALIDATE_PRICE_URL = (
    "https://test_url/api/Itinerary/Validate/{pricing_id}/{transaction_id}"
)

_ARN_LHR_CRITERIA = amqp_pb2.Criteria(
    origin_iata="ARN",
    destination_iata="LHR",
    outbound_departure=protobuf.datetime_to_protobuf_datetime(
        datetime.datetime(
            year=2022,
            month=11,
            day=1,
            hour=19,
            minute=40,
            second=0,
            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
        ),
    ),
    cabin_class="Economy",
    adults=1,
)
_ARN_LHR = amqp_pb2.SearchCriteriaTask(
    offer_search_id="FOO",
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
                            2022,
                            11,
                            1,
                            19,
                            40,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        datetime.datetime(
                            2022,
                            11,
                            1,
                            21,
                            20,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/London"),
                        ),
                    ),
                ),
            ],
        ),
    ],
    criteria=_ARN_LHR_CRITERIA,
)
_ARN_LHR_NO_RESULTS = amqp_pb2.SearchCriteriaTask(
    offer_search_id="FOO",
    segments=[
        models_pb2.Segment(),
    ],
    criteria=_ARN_LHR_CRITERIA,
)


def _mock_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    origin: str,
    destination: str,
    departure_date: str,
) -> None:
    prefix = "{origin}_{destination}_{date}".format(
        origin=origin,
        destination=destination,
        date=departure_date,
    )

    search_response = conftest.load_json_fixture(
        "{prefix}_post_search".format(prefix=prefix),
    )

    httpx_mock.add_response(
        method="POST",
        json=search_response,
        url="https://test_url/api/search",
    )

    itinerary_validate_response = conftest.load_json_fixture(
        "{prefix}_post_itinerary_validate".format(prefix=prefix),
    )

    httpx_mock.add_response(
        method="POST",
        json=itinerary_validate_response,
        url="https://test_url/api/Itinerary/Validate",
    )

    branded_itinerary_response = conftest.load_json_fixture(
        "{prefix}_get_itinerary_validate_{id}_{transaction_id}".format(
            prefix=prefix,
            id=itinerary_validate_response["id"],
            transaction_id=itinerary_validate_response["transactionId"],
        ),
    )

    httpx_mock.add_response(
        method="GET",
        json=branded_itinerary_response,
        url=_VALIDATE_PRICE_URL.format(
            pricing_id="d0801a2f80af41da9a283614e6d02b6a",
            transaction_id=search_response["transactionId"],
        ),
    )

    _mock_search_responses(
        httpx_mock,
        prefix,
        search_response,
        itinerary_validate_response,
        branded_itinerary_response,
    )


def _mock_search_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    prefix: str,
    search_response: Mapping[str, Any],
    itinerary_validate_response: Mapping[str, Any],
    branded_itinerary_response: Mapping[str, Any],
) -> None:
    for page in range(10):
        try:
            offer_response = conftest.load_json_fixture(
                "{prefix}_get_search_{id}_{transaction}_{page}.json".format(
                    prefix=prefix,
                    id=search_response["id"],
                    transaction=search_response["transactionId"],
                    page=page,
                ),
            )
        except FileNotFoundError:
            break

        httpx_mock.add_response(
            method="GET",
            json=offer_response,
            url=_OFFER_URL.format(
                id=search_response["id"],
                transaction=search_response["transactionId"],
                page=page,
            ),
        )

        offer = offer_response["flight"][0]
        for brand in branded_itinerary_response["itinerary"]["brandedFares"]:
            httpx_mock.add_response(
                method="PUT",
                json=conftest.load_json_fixture(
                    (
                        "{prefix}_put_itinerary_{id}_{offer}_price?"
                        + "transactionid={transaction_id}&brandid={brand_id}.json"
                    ).format(
                        prefix=prefix,
                        id=itinerary_validate_response["id"],
                        offer=offer["id"],
                        transaction_id=search_response["transactionId"],
                        brand_id=brand["brandId"].lower(),
                    ),
                ),
                url=_PRICE_URL.format(
                    id=itinerary_validate_response["id"],
                    offer=offer["id"],
                    transaction_id=search_response["transactionId"],
                    brand_id=brand["brandId"],
                ),
            )


@pytest.mark.parametrize(
    "criteria, expected",
    [
        (_ARN_LHR, 1),
        (_ARN_LHR_NO_RESULTS, 0),
    ],
)
async def test_number_of_results(
    ask2go_adapter: adapter.Ask2GoAdapter,
    httpx_mock: pytest_httpx.HTTPXMock,
    criteria: amqp_pb2.SearchCriteriaTask,
    expected: int,
) -> None:
    _mock_responses(
        httpx_mock,
        criteria.criteria.origin_iata,
        criteria.criteria.destination_iata,
        str(protobuf.protobuf_to_date(criteria.criteria.outbound_departure)),
    )
    search_results = ask2go_adapter.gather_search_results(criteria)
    count = sum([1 async for _ in search_results])

    assert count == expected


async def test_search_result_data(  # noqa: WPS218
    ask2go_adapter: adapter.Ask2GoAdapter,
    offer_transformer: transformer.OfferTransformer,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    _mock_responses(
        httpx_mock,
        _ARN_LHR.criteria.origin_iata,
        _ARN_LHR.criteria.destination_iata,
        str(protobuf.protobuf_to_date(_ARN_LHR.criteria.outbound_departure)),
    )

    offer_groups = offer_transformer.offer_prices_to_offer_groups(
        _ARN_LHR,
        ask2go_adapter.gather_search_results(_ARN_LHR),
    )

    async for offer_group in offer_groups:
        assert offer_group.offer_search_id == _ARN_LHR.offer_search_id
        segment = offer_group.segments[0]
        _assert_offer(offer_group.offers[0], segment.id)
        assert segment.segment_id == "segment_id"
        assert segment.operator == "SK"
        assert segment.vendor == "SK"
        assert segment.terminal == "5"
        assert segment.vehicle.equipment == "32N"
        assert segment.vehicle.number == "1527"
        assert segment.type == models_pb2.Schedule.TYPE_AIR
        leg = segment.legs[0]
        assert leg.id == "leg_id"
        assert leg.origin.ref == "ARN"
        assert leg.origin.name == "Arlanda"
        assert leg.origin.time_zone == "Europe/Stockholm"
        assert math.isclose(leg.origin.coordinates.latitude, 59.650831)
        assert math.isclose(leg.origin.coordinates.longitude, 17.92119)
        assert leg.destination.ref == "LHR"
        assert leg.destination.name == "Heathrow"
        assert leg.destination.time_zone == "Europe/London"
        assert math.isclose(leg.destination.coordinates.latitude, 51.470311)
        assert math.isclose(leg.destination.coordinates.longitude, -0.458118)
        expected_leg = _ARN_LHR.segments[0].legs[0]
        assert leg.departure_at == expected_leg.departure_at
        assert leg.arrival_at == expected_leg.arrival_at


def _assert_offer(offer: offers_pb2.Offer, expected_segment_id: str) -> None:
    segment_details = offer.segment_details[0]
    assert segment_details.offer_segment_id == expected_segment_id
    assert segment_details.cabin_class.marketing_name == "Economy"
    assert segment_details.cabin_class.type == models_pb2.CabinClass.TYPE_ECONOMY
    assert offer.price.amount == 126184
    assert offer.price.currency == "EUR"


@pytest.mark.parametrize(
    "departure_time, expected",
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
    assert adapter.time_to_window(departure_time) == expected
