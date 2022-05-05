import datetime
import math
import zoneinfo
from typing import Any, Mapping

import pytest
import pytest_httpx

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.junction.providers.ask2go import adapter
from snowfall.junction.providers.ask2go.v1alpha import amqp_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import filesystem

_FIXTURE_PATH = "python/snowfall/junction/providers/ask2go/fixtures/{path}"
_OFFER_URL = "https://test_url/api/search/{id}/{transaction}/{page}"
_PRICE_URL = (
    "https://test_url/api/Itinerary/{id}/{offer}/Price?transactionId={transaction}"
)

_ARN_LHR_CRITERIA = amqp_pb2.Criteria(
    origin_iata="ARN",
    destination_iata="LHR",
    outbound=protobuf.datetime_to_protobuf_datetime(
        datetime.datetime(
            2022,
            5,
            24,
            7,
            50,
            0,
            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
        ),
    ),
    cabin_class="Any",
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
                            5,
                            24,
                            7,
                            50,
                            0,
                            tzinfo=zoneinfo.ZoneInfo("Europe/Stockholm"),
                        ),
                    ),
                    arrival_at=protobuf.datetime_to_protobuf(
                        datetime.datetime(
                            2022,
                            5,
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
    loader = filesystem.FileLoader()
    prefix = "{origin}_{destination}_{date}".format(
        origin=origin,
        destination=destination,
        date=departure_date,
    )

    search_response = loader.load(
        _FIXTURE_PATH.format(
            path="{prefix}_search.json".format(prefix=prefix),
        ),
    )

    httpx_mock.add_response(
        method="POST",
        json=search_response,
        url="https://test_url/api/search",
    )

    _mock_search_responses(httpx_mock, prefix, search_response, loader)


def _mock_search_responses(
    httpx_mock: pytest_httpx.HTTPXMock,
    prefix: str,
    search_response: Mapping[str, Any],
    loader: filesystem.Loader,
) -> None:
    for page in range(10):
        try:
            offer_response = loader.load(
                _FIXTURE_PATH.format(
                    path="{prefix}_search_{id}_{transaction}_{page}.json".format(
                        prefix=prefix,
                        id=search_response["id"],
                        transaction=search_response["transactionId"],
                        page=page,
                    ),
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

        for offer in offer_response["flight"]:
            httpx_mock.add_response(
                method="PUT",
                json=loader.load(
                    _FIXTURE_PATH.format(
                        path="{prefix}_itinerary_{id}_{offer}_price.json".format(
                            prefix=prefix,
                            id=search_response["id"],
                            offer=offer["id"],
                        ),
                    ),
                ),
                url=_PRICE_URL.format(
                    id=search_response["id"],
                    offer=offer["id"],
                    transaction=search_response["transactionId"],
                ),
            )


@pytest.mark.asyncio
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
        str(protobuf.protobuf_to_date(criteria.criteria.outbound)),
    )
    search_results = ask2go_adapter.gather_search_results(criteria)
    count = sum([1 async for _ in search_results])

    assert count == expected


@pytest.mark.asyncio
async def test_search_result_data(  # noqa: WPS218
    ask2go_adapter: adapter.Ask2GoAdapter,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    _mock_responses(
        httpx_mock,
        _ARN_LHR.criteria.origin_iata,
        _ARN_LHR.criteria.destination_iata,
        str(protobuf.protobuf_to_date(_ARN_LHR.criteria.outbound)),
    )

    async for search_result in ask2go_adapter.gather_search_results(_ARN_LHR):
        assert search_result.offer_search_id == _ARN_LHR.offer_search_id
        _assert_offer(search_result.offers[0])
        segment = search_result.segments[0]
        assert segment.id == "segment_id"
        assert segment.operator == "SK"
        assert segment.vendor == "SK"
        assert segment.terminal == "5"
        assert segment.vehicle.equipment == "32N"
        assert segment.vehicle.number == "525"
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


def _assert_offer(offer: offers_pb2.Offer) -> None:
    segment_details = offer.segment_details[0]
    assert segment_details.id == "segment_id"
    assert segment_details.cabin_class.marketing_name == "Economy"
    assert segment_details.cabin_class.type == models_pb2.CabinClass.TYPE_ECONOMY
    assert offer.price.amount == 6374
    assert offer.price.currency == "EUR"
