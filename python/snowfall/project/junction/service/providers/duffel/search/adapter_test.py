from collections.abc import Mapping, Sequence

import pytest
import pytest_httpx

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.duffel.conftest import (
    API_BASE_URL,
    load_file_fixture,
    search_task_from_offer,
)
from snowfall.project.junction.service.providers.duffel.search import adapter
from snowfall.project.junction.service.providers.duffel.v1.amqp_pb2 import (
    SearchCriteriaTask,
)
from snowfall.stdlib import money
from snowfall.vendor.duffel.models.offer import PrivateFare
from snowfall.vendor.duffel.models.offer_request import OfferRequestResponse


async def get_search_task_for_fixture(
    httpx_mock: pytest_httpx.HTTPXMock,
    name: str,
) -> SearchCriteriaTask:
    json = await load_file_fixture(name)
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.model_validate(json)
    return search_task_from_offer(offer_response.response_data.offers[0])


async def test_adapter(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.DuffelSearchAdapter,
) -> None:
    search_task = await get_search_task_for_fixture(
        httpx_mock,
        "offer_request_response.json",
    )

    offer_groups = [
        offer_group
        async for offer_group in search_adapter.gather_search_results(
            search_adapter.search_criteria_generator(search_task),
        )
    ]

    offers = offer_groups[0].offers
    assert [offer.brand_name for offer in offers] == [
        "Economy Light",
        "Economy Essential",
    ]
    assert [offer.baggage_allowances[0].free for offer in offers] == [True, True]


async def test_offer_with_stop(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.DuffelSearchAdapter,
) -> None:
    json = await load_file_fixture("offers_with_stop.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.model_validate(json)
    offer = offer_response.response_data.offers[0]
    search_task = search_task_from_offer(offer)

    offer_groups = [
        offer_group
        async for offer_group in search_adapter.gather_search_results(
            search_adapter.search_criteria_generator(search_task),
        )
    ]

    assert all(
        offer_group.segments[0].legs[0].origin.name  # noqa: WPS219
        == "Heathrow Airport"
        for offer_group in offer_groups
    )
    assert all(
        offer_group.segments[-1].legs[-1].destination.name  # noqa: WPS219
        == "Sydney Airport"
        for offer_group in offer_groups
    )

    assert len(offer_groups[0].segments) == 2


async def test_airline_validator(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter_no_ba: adapter.DuffelSearchAdapter,
    search_adapter_ba_only: adapter.DuffelSearchAdapter,
) -> None:
    json = await load_file_fixture("offers_with_stop.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.model_validate(json)
    ba15_offer = next(
        offer
        for offer in offer_response.response_data.offers
        if all(
            segment.marketing_carrier_flight_number == "0015"
            for offer_slice in offer.slices
            for segment in offer_slice.segments
        )
    )

    search_task = search_task_from_offer(ba15_offer)

    offer_groups = [
        offer_group
        async for offer_group in search_adapter_no_ba.gather_search_results(
            search_adapter_no_ba.search_criteria_generator(search_task),
        )
    ]

    assert len(offer_groups) == 24

    offer_groups = [
        offer_group
        async for offer_group in search_adapter_ba_only.gather_search_results(
            search_adapter_ba_only.search_criteria_generator(search_task),
        )
    ]

    assert len(offer_groups) == 7

    vs23_offer = next(
        offer
        for offer in offer_response.response_data.offers
        if any(
            segment.marketing_carrier_flight_number == "23"
            for offer_slice in offer.slices
            for segment in offer_slice.segments
        )
    )

    search_task = search_task_from_offer(vs23_offer)

    offer_groups = [
        offer_group
        async for offer_group in search_adapter_no_ba.gather_search_results(
            search_adapter_no_ba.search_criteria_generator(search_task),
        )
    ]

    assert len(offer_groups) == 24

    offer_groups = [
        offer_group
        async for offer_group in search_adapter_ba_only.gather_search_results(
            search_adapter_ba_only.search_criteria_generator(search_task),
        )
    ]

    assert len(offer_groups) == 7


@pytest.mark.parametrize(
    "fares",
    [
        {
            "QF": [
                PrivateFare(corporate_code="C1", tracking_reference="TR1"),
                PrivateFare(corporate_code="C2", tracking_reference="TR2"),
            ],
            "TF": [
                PrivateFare(corporate_code="C1", tracking_reference="TR1"),
                PrivateFare(corporate_code="C2", tracking_reference="TR2"),
            ],
        },
        {
            "TF": [
                PrivateFare(corporate_code="C2", tracking_reference="TR2"),
                PrivateFare(corporate_code="C1", tracking_reference="TR1"),
            ],
            "QF": [
                PrivateFare(corporate_code="C2", tracking_reference="TR2"),
                PrivateFare(corporate_code="C1", tracking_reference="TR1"),
            ],
        },
    ],
)
def test_adapter_cache_generate(fares: Mapping[str, Sequence[PrivateFare]]) -> None:
    expected = [
        "QF-corporate_code-C1\x00tracking_reference-TR1\x00tour_code-None\x00fare_type-None\x00corporate_code-C2\x00tracking_reference-TR2\x00tour_code-None\x00fare_type-None",
        "TF-corporate_code-C1\x00tracking_reference-TR1\x00tour_code-None\x00fare_type-None\x00corporate_code-C2\x00tracking_reference-TR2\x00tour_code-None\x00fare_type-None",
    ]
    assert adapter._generate_private_fares_keys(fares) == expected  # noqa: SLF001


async def test_private_fares_and_specific_token(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.DuffelSearchAdapter,
) -> None:
    search_task = await get_search_task_for_fixture(
        httpx_mock,
        "offer_request_response.json",
    )

    search_task.criteria.reseller_id = "res1"
    search_criteria_wrapper = search_adapter.search_criteria_generator(search_task)
    private_fares = search_criteria_wrapper.search_criteria.offer_data.private_fares
    assert private_fares == {
        "QF": [PrivateFare(corporate_code="FLX53", tracking_reference="ABN:2345678")],
    }

    offer_groups = [
        offer_group
        async for offer_group in search_adapter.gather_search_results(
            search_criteria_wrapper,
        )
    ]

    assert offer_groups
    assert httpx_mock.get_requests()[0].headers["authorization"] == "Bearer token1"


async def test_offer_price_breakdown(  # noqa: WPS218
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.DuffelSearchAdapter,
) -> None:
    search_task = await get_search_task_for_fixture(
        httpx_mock,
        "offer_request_response.json",
    )

    offer_groups = [
        offer_group
        async for offer_group in search_adapter.gather_search_results(
            search_adapter.search_criteria_generator(search_task),
        )
    ]

    offer = offer_groups[0].offers[0]

    base_fare = offer.price_breakdown[0]
    base_fare_price = money.from_protobuf(base_fare.price)
    assert str(base_fare_price) == "195.57"
    assert base_fare_price.currency.code == "GBP"
    assert (
        base_fare.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    tax = offer.price_breakdown[1]
    tax_price = money.from_protobuf(tax.price)
    assert str(tax_price) == "306.86"
    assert tax_price.currency.code == "GBP"
    assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX
