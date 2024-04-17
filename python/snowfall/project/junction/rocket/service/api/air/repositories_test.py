from typing import Any

import pytest

from snowfall.project.junction.rocket.service.api.air.models import (
    AirSearchResult,
    FareTypeEnum,
    Offer,
    Price,
)
from snowfall.project.junction.rocket.service.api.air.repositories import (
    AirSearchResultRepository,
)

UUID = "eaaf5ab5-64f3-4190-a6a7-d4b40e6010b2"
SEARCH_ID = "c7384289-a633-4bb3-83c6-3aafcb20a4ad"
OUTBOUND_SEARCH_OFFER_ID = "a7384289-a633-4bb3-83c6-3aafcb20a4zz"
FLIGHT_REF_ID = "1P0_1234ABC"


@pytest.fixture()
def example_air_search_result() -> Any:
    return AirSearchResult(
        id=UUID,
        search_id=SEARCH_ID,
        provider_id="",
        offers=[],
        result_details=[],
    )


@pytest.fixture()
def example_air_search_result_with_offers() -> Any:
    return AirSearchResult(
        id=UUID,
        search_id=SEARCH_ID,
        provider_id="",
        offers=[
            Offer(
                id=OUTBOUND_SEARCH_OFFER_ID,
                price=Price(price=1.0, currency=""),
                fare_type=FareTypeEnum.basic,
                cabin_details=None,
                name="",
                ref_ids=[
                    FLIGHT_REF_ID,
                ],
            ),
        ],
        result_details=[],
    )


async def test_find_result_exists_by_search_id(
    air_search_repo: AirSearchResultRepository,
    example_air_search_result: AirSearchResult,
) -> None:
    await air_search_repo.insert(example_air_search_result)

    results_response = await air_search_repo.find_any_result_by_search_id(SEARCH_ID)
    assert results_response


async def test_find_results_by_search_id(
    air_search_repo: AirSearchResultRepository,
    example_air_search_result: AirSearchResult,
) -> None:
    await air_search_repo.insert(example_air_search_result)

    results_response = await air_search_repo.find_results_by_search_id(SEARCH_ID)
    assert results_response is not None
    async for result in results_response:
        assert result == example_air_search_result


async def test_find_result_by_outbound_offer_id(
    air_search_repo: AirSearchResultRepository,
    example_air_search_result_with_offers: AirSearchResult,
) -> None:
    await air_search_repo.insert(example_air_search_result_with_offers)

    result = await air_search_repo.find_result_by_offer_id(
        OUTBOUND_SEARCH_OFFER_ID,
    )
    assert result is not None
    assert result == example_air_search_result_with_offers
    assert result.search_id == SEARCH_ID

    assert result.offers

    selected_offers = [
        offer for offer in result.offers if offer.id == OUTBOUND_SEARCH_OFFER_ID
    ]
    assert selected_offers[0].ref_ids == [FLIGHT_REF_ID]
