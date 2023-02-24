import pytest_httpx

from snowfall.project.junction.service.providers.duffel.conftest import (
    API_BASE_URL,
    load_file_fixture,
    search_task_from_offer,
)
from snowfall.project.junction.service.providers.duffel.search import adapter
from snowfall.vendor.duffel.models.offer_request import OfferRequestResponse


async def test_adapter(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.DuffelSearchAdapter,
) -> None:
    json = load_file_fixture("offer_request_response.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.parse_obj(json)
    search_task = search_task_from_offer(offer_response.response_data.offers[0])

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
    json = load_file_fixture("offers_with_stop.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.parse_obj(json)
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


async def test_airline_validator(  # noqa: WPS210
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter_no_ba: adapter.DuffelSearchAdapter,
    search_adapter_ba_only: adapter.DuffelSearchAdapter,
) -> None:
    json = load_file_fixture("offers_with_stop.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/air/offer_requests".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_response = OfferRequestResponse.parse_obj(json)
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
