from datetime import datetime
from typing import Any

import pytest

from snowfall.project.junction.rocket.service.api.flights.models import (
    CabinDetails,
    FareTypeEnum,
    FlightSearchResult,
    Offer,
    Price,
    ResultDetails,
)
from snowfall.project.junction.rocket.service.api.flights.repositories import (
    FlightSearchResultRepository,
)

UUID = "eaaf5ab5-64f3-4190-a6a7-d4b40e6010b2"
SEARCH_ID = "c7384289-a633-4bb3-83c6-3aafcb20a4ad"
OUTBOUND_SEARCH_OFFER_ID = "a7384289-a633-4bb3-83c6-3aafcb20a4dc"
OUTBOUND_SEARCH_OFFER_ID2 = "eeb00249-288d-446c-9506-438779741eb4"
RESULT_DETAILS_ID = "7434860a-0ee5-4639-8bce-9b48a3ecbc78"
RESULT_DETAILS_ID2 = "71da417d-450d-4462-80e2-9b44c980e9e4"
FLIGHT_REF_ID = "1P0_1234ABC"


@pytest.fixture()
def example_flight_search_result() -> Any:
    return FlightSearchResult(
        id=UUID,
        search_id=SEARCH_ID,
        provider_id="",
        offers=[],
        result_details=[],
    )


@pytest.fixture()
def example_flight_search_result_one() -> Any:
    return FlightSearchResult(
        id=UUID,
        search_id=SEARCH_ID,
        provider_id="",
        offers=[
            Offer(
                id=OUTBOUND_SEARCH_OFFER_ID,
                price=Price(price=13.37, currency="EUR"),
                fare_type=FareTypeEnum("1"),
                cabin_details=[
                    CabinDetails(
                        id="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                        result_detail_id=RESULT_DETAILS_ID,
                        marketing_name="Economy",
                    ),
                ],
                name="Economy Basic",
                ref_ids=[
                    FLIGHT_REF_ID,
                ],
            ),
        ],
        result_details=[
            ResultDetails(
                id=RESULT_DETAILS_ID,
                flight_number="flight_number",
                marketing_airline="marketing_airline",
                arrival_station="arrival_station",
                departure_station="departure_station",
                departure_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                arrival_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                duration=123,
                segment_key="segment_key",
                operating_airline="operating_airline",
            ),
        ],
    )


@pytest.fixture()
def example_flight_search_result_two() -> Any:
    return FlightSearchResult(
        id=UUID,
        search_id=SEARCH_ID,
        provider_id="",
        offers=[
            Offer(
                id=OUTBOUND_SEARCH_OFFER_ID,
                price=Price(price=13.37, currency="EUR"),
                fare_type=FareTypeEnum("1"),
                cabin_details=[
                    CabinDetails(
                        id="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                        result_detail_id=RESULT_DETAILS_ID,
                        marketing_name="Economy",
                    ),
                ],
                name="Economy Basic",
                ref_ids=[
                    FLIGHT_REF_ID,
                ],
            ),
            Offer(
                id=OUTBOUND_SEARCH_OFFER_ID2,
                price=Price(price=13.37, currency="EUR"),
                fare_type=FareTypeEnum("1"),
                cabin_details=[
                    CabinDetails(
                        id="04f83af9-90bb-4a0f-9881-03e1e690f7f5",
                        result_detail_id=RESULT_DETAILS_ID2,
                        marketing_name="Economy2",
                    ),
                ],
                name="Economy Basic2",
                ref_ids=[
                    FLIGHT_REF_ID,
                ],
            ),
        ],
        result_details=[
            ResultDetails(
                id=RESULT_DETAILS_ID,
                flight_number="flight_number",
                marketing_airline="marketing_airline",
                arrival_station="arrival_station",
                departure_station="departure_station",
                departure_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                arrival_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                duration=123,
                segment_key="segment_key",
                operating_airline="operating_airline",
            ),
            ResultDetails(
                id=RESULT_DETAILS_ID2,
                flight_number="flight_number2",
                marketing_airline="marketing_airline2",
                arrival_station="arrival_station2",
                departure_station="departure_station2",
                departure_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                arrival_at=datetime.fromisoformat("2024-03-24T00:00:00Z"),
                duration=123,
                segment_key="segment_key2",
                operating_airline="operating_airline2",
            ),
        ],
    )


async def test_find_result_exists_by_search_id(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result)

    results_response = await flights_search_repo.find_any_result_by_search_id(SEARCH_ID)
    assert results_response


async def test_find_results_by_search_id(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result)

    results_response = await flights_search_repo.find_results_by_search_id(SEARCH_ID)
    assert results_response is not None
    async for result in results_response:
        assert result == example_flight_search_result


async def test_find_result_by_outbound_offer_id(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result_one: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result_one)

    result = await flights_search_repo.find_result_by_offer_id(
        OUTBOUND_SEARCH_OFFER_ID,
    )
    assert result is not None
    assert result == example_flight_search_result_one
    assert result.search_id == SEARCH_ID

    assert result.offers

    selected_offers = [
        offer for offer in result.offers if offer.id == OUTBOUND_SEARCH_OFFER_ID
    ]
    assert selected_offers[0].ref_ids == [FLIGHT_REF_ID]


async def test_find_results_by_multiple_outbound_offer_ids(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result_two: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result_two)

    example_new = example_flight_search_result_two
    example_new.id = "70c57962-0596-4663-8c3a-1730442c1f4c"
    await flights_search_repo.insert(example_new)

    offer_id_inputs = [OUTBOUND_SEARCH_OFFER_ID, OUTBOUND_SEARCH_OFFER_ID2]
    results_response = await flights_search_repo.find_results_by_offer_ids(
        offer_id_inputs,
    )
    assert results_response is not None

    result_ids = []
    offer_ids = []
    async for result in results_response:
        result_ids.append(result.id)
        offer_ids.extend([offer.id for offer in result.offers])

    offer_ids_set = set(offer_ids)
    assert len(set(result_ids)) == 2
    assert len(offer_ids_set) == 2

    for offer_id in offer_id_inputs:
        assert offer_id in offer_ids_set

    for result_id in (example_flight_search_result_two.id, example_new.id):
        assert result_id in result_ids


async def test_find_result_by_result_detail_id(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result_one: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result_one)

    result = await flights_search_repo.find_result_by_result_detail_id(
        RESULT_DETAILS_ID,
    )
    assert result is not None
    assert result == example_flight_search_result_one
    assert result.search_id == SEARCH_ID

    assert result.result_details


async def test_find_results_by_multiple_result_detail_ids(
    flights_search_repo: FlightSearchResultRepository,
    example_flight_search_result_two: FlightSearchResult,
) -> None:
    await flights_search_repo.insert(example_flight_search_result_two)

    example_new = example_flight_search_result_two
    example_new.id = "70c57962-0596-4663-8c3a-1730442c1f4c"
    await flights_search_repo.insert(example_new)

    result_detail_id_inputs = [RESULT_DETAILS_ID, RESULT_DETAILS_ID2]
    results_response = await flights_search_repo.find_results_by_result_detail_ids(
        result_detail_id_inputs,
    )
    assert results_response is not None

    result_ids = []
    result_detail_ids = []
    async for result in results_response:
        result_ids.append(result.id)
        result_detail_ids.extend([
            result_detail.id for result_detail in result.result_details
        ])

    result_detail_ids_set = set(result_detail_ids)
    assert len(set(result_ids)) == 2
    assert len(result_detail_ids_set) == 2

    for result_detail_id in result_detail_id_inputs:
        assert result_detail_id in result_detail_ids_set

    for result_id in (example_flight_search_result_two.id, example_new.id):
        assert result_id in result_ids
