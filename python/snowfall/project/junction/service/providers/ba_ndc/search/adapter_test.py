import pytest_httpx

from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offers_pb2
from snowfall.project.junction.service.providers.ba_ndc.conftest import (
    API_BASE_URL,
    load_file_fixture,
    search_task_from_offer,
)
from snowfall.project.junction.service.providers.ba_ndc.search import adapter
from snowfall.project.junction.service.providers.ba_ndc.v1alpha.amqp_pb2 import (
    SearchCriteriaTask,
)
from snowfall.stdlib import money
from snowfall.vendor.ba_ndc.adapters.offers_response_adapter import (
    OffersResponseAdapter,
)
from snowfall.vendor.ba_ndc.models.response_offer_search_schemas import (
    OfferSearchResponse,
)


async def get_search_task_for_fixture(
    httpx_mock: pytest_httpx.HTTPXMock,
    name: str,
) -> SearchCriteriaTask | None:
    json = await load_file_fixture(name)
    assert json is not None

    httpx_mock.add_response(
        url="{api_base_url}/offers".format(
            api_base_url=API_BASE_URL,
        ),
        method="POST",
        json=json,
    )

    offer_adapter = OffersResponseAdapter(OfferSearchResponse.parse_obj(json))
    return search_task_from_offer(offer_adapter)


async def test_adapter(
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.BaNdcSearchAdapter,
) -> None:
    search_task = await get_search_task_for_fixture(
        httpx_mock,
        "get_offers_response.json",
    )

    if search_task is not None:
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


async def test_offer_price_breakdown(  # noqa: WPS218
    httpx_mock: pytest_httpx.HTTPXMock,
    search_adapter: adapter.BaNdcSearchAdapter,
) -> None:
    search_task = await get_search_task_for_fixture(
        httpx_mock,
        "get_offers_response.json",
    )

    if search_task is not None:
        offer_groups = [
            offer_group
            async for offer_group in search_adapter.gather_search_results(
                search_adapter.search_criteria_generator(search_task),
            )
        ]

        offer = offer_groups[0].offers[0]

        base_fare = offer.price_breakdown[0]
        base_fare_price = money.from_protobuf(base_fare.price)
        assert str(base_fare_price) == "14.00"
        assert base_fare_price.currency.code == "EUR"
        assert (
            base_fare.breakdown_type
            == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
        )

        tax = offer.price_breakdown[1]
        tax_price = money.from_protobuf(tax.price)
        assert str(tax_price) == "35.46"
        assert tax_price.currency.code == "EUR"
        assert tax.breakdown_type == offers_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX
