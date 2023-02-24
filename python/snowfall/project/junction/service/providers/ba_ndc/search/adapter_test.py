import pytest_httpx

from snowfall.project.junction.service.providers.ba_ndc.conftest import (
    API_BASE_URL,
    load_file_fixture,
    search_task_from_offer,
)
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.models.response_offer_search_schemas import (
    OfferSearchResponse,
)


async def test_adapter(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.BaNdcSearchAdapter,
) -> None:
    json = load_file_fixture("get_offers_response.json")
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/offers".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_adapter = OffersResponseAdapter(OfferSearchResponse.parse_obj(json))
    search_task = search_task_from_offer(offer_adapter)

    if search_task:
        offer_groups = [
            offer_group
            async for offer_group in search_adapter.gather_search_results(
                search_adapter.search_criteria_generator(search_task),
            )
        ]

        assert len(offer_groups) == 15
        assert len(offer_groups[0].offers) == 4
        assert offer_groups[0].offers[0].brand_name == "BASIC"
        assert offer_groups[0].offers[2].brand_name == "PLUS SELECT"
