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
from snowfall.stdlib import money
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
_ARN_LHR_PRICE_FAILURE = amqp_pb2.SearchCriteriaTask(
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
                            24,
                            7,
                            45,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        datetime.datetime(
                            2022,
                            11,
                            24,
                            9,
                            35,
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
                year=2022,
                month=11,
                day=24,
                hour=7,
                minute=45,
                second=0,
                tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
            ),
        ),
        cabin_class="Any",
        adults=1,
    ),
)


def _mock_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    origin: str,
    destination: str,
    departure_date: datetime.date,
) -> None:
    prefix = "{origin}_{destination}_{date}".format(
        origin=origin,
        destination=destination,
        date=str(departure_date),
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
        status_code=202,
        url=_VALIDATE_PRICE_URL.format(
            pricing_id=itinerary_validate_response["id"],
            transaction_id=search_response["transactionId"],
        ),
    )

    httpx_mock.add_response(
        method="GET",
        json=branded_itinerary_response,
        url=_VALIDATE_PRICE_URL.format(
            pricing_id=itinerary_validate_response["id"],
            transaction_id=search_response["transactionId"],
        ),
    )

    _mock_pricing(httpx_mock, prefix)
    _mock_search_responses(
        httpx_mock,
        prefix,
        search_response,
    )


def _mock_pricing(httpx_mock: pytest_httpx.HTTPXMock, prefix: str) -> None:
    try:
        price_async_response = conftest.load_json_fixture(
            "{prefix}_put_itinerary_priceasync".format(prefix=prefix),
        )
    except FileNotFoundError:
        return

    httpx_mock.add_response(
        method="PUT",
        json=price_async_response,
        url="https://test_url/api/Itinerary/PriceAsync",
    )

    pricing_response = conftest.load_json_fixture(
        "{prefix}_get_itinerary_{id}_{transaction_id}_getprice".format(
            prefix=prefix,
            id=price_async_response["id"],
            transaction_id=price_async_response["transactionId"],
        ),
    )

    httpx_mock.add_response(
        method="GET",
        json=pricing_response,
        url="https://test_url/api/Itinerary/{id}/{transaction_id}/GetPrice".format(
            id=price_async_response["id"],
            transaction_id=price_async_response["transactionId"],
        ),
    )


def _mock_search_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    prefix: str,
    search_response: Mapping[str, Any],
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
        protobuf.protobuf_to_date(criteria.criteria.outbound_departure),
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
        protobuf.protobuf_to_date(_ARN_LHR.criteria.outbound_departure),
    )

    offer_groups = offer_transformer.offer_prices_to_offer_groups(
        _ARN_LHR,
        ask2go_adapter.gather_search_results(_ARN_LHR),
    )

    async for offer_group in offer_groups:
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


def _assert_offer(offer: offers_pb2.Offer, expected_segment_id: str) -> None:
    segment_details = offer.segment_details[0]
    assert segment_details.offer_segment_id == expected_segment_id
    assert segment_details.cabin_class.marketing_name == "Economy"
    assert segment_details.cabin_class.type == models_pb2.CabinClass.TYPE_ECONOMY
    price = money.from_protobuf(offer.price)
    assert price.amount == 126184
    assert price.currency.code == "EUR"


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


async def test_price_failure_still_returns_options(
    ask2go_adapter: adapter.Ask2GoAdapter,
    offer_transformer: transformer.OfferTransformer,
    magic_mocker: conftest.MagicMocker,
) -> None:
    with magic_mocker.with_fixture_path("price_failure"):
        offer_groups = offer_transformer.offer_prices_to_offer_groups(
            _ARN_LHR_PRICE_FAILURE,
            ask2go_adapter.gather_search_results(_ARN_LHR_PRICE_FAILURE),
        )

        async for offer_group in offer_groups:
            for offer in offer_group.offers:
                assert offer.brand_name == "SAS PLUS FULL FLEX"


async def test_price_timeout_still_returns_options(
    ask2go_adapter: adapter.Ask2GoAdapter,
    offer_transformer: transformer.OfferTransformer,
    magic_mocker: conftest.MagicMocker,
) -> None:
    with magic_mocker.with_fixture_path("price_timeout"):
        offer_groups = offer_transformer.offer_prices_to_offer_groups(
            _ARN_LHR_PRICE_FAILURE,
            ask2go_adapter.gather_search_results(_ARN_LHR_PRICE_FAILURE),
        )

        async for offer_group in offer_groups:
            for offer in offer_group.offers:
                assert offer.brand_name == "SAS PLUS FULL FLEX"
