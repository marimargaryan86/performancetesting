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
        async for offer_group in search_adapter.gather_search_results(search_task)
    ]

    offers = [offer for group in offer_groups for offer in group.offers]
    assert [offer.brand_name for offer in offers] == [
        "Economy Light",
        "Economy Essential",
    ]
    assert [
        [segment.baggage_allowances[0].free for segment in offer.segment_details]
        for offer in offers
    ] == [[True, True], [True, True]]
