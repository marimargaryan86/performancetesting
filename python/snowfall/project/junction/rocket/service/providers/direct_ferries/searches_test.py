import datetime

import pytest

from snowfall.project.junction.rocket.service.providers.direct_ferries import (
    searches,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2


@pytest.mark.skip(reason="integration test")
async def test_one_way_search_integration(
    generator: searches.SearchResultGenerator,
    one_way_search: models_pb2.Search,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(one_way_search)
    quotes = generator.generate(search_criteria[0])
    offers = [quote async for quote in quotes]

    assert offers


@pytest.mark.skip(reason="integration test")
async def test_round_trip_initial_search_integration(
    generator: searches.SearchResultGenerator,
    round_trip_search: models_pb2.Search,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(round_trip_search)
    quotes = generator.generate(search_criteria[0])
    offers = [quote async for quote in quotes]

    assert offers


@pytest.mark.skip(reason="integration test")
async def test_return_trip_search_integration(
    generator: searches.SearchResultGenerator,
    round_trip_search: models_pb2.Search,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    initial_search_criteria = criteria_generator.criteria_task_generator(
        round_trip_search,
    )
    quotes = generator.generate(initial_search_criteria[0])
    initial_offers = [quote async for quote in quotes]

    round_trip_search.ferry.outbound_offer_id = initial_offers[0].offers[0].id
    return_search_criteria = criteria_generator.criteria_task_generator(
        round_trip_search,
    )
    return_quotes = generator.generate(return_search_criteria[0])
    return_offers = [return_quote async for return_quote in return_quotes]

    assert return_offers


async def test_one_way_search(  # noqa: WPS218
    generator: searches.SearchResultGenerator,
    mock_one_way_search: models_pb2.Search,
    mock_one_way_response: None,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(mock_one_way_search)
    quotes = generator.generate(search_criteria[0])
    offers = [quote async for quote in quotes]
    assert len(offers) == 2

    offer = offers[0].offers[0]
    assert offer.price.units == 104

    assert len(offers[0].result_details) == 1

    result_details = offers[0].result_details[0]
    assert result_details.ferry.origin.ref == "NLMDK"
    assert result_details.ferry.destination.ref == "GBHRW"
    assert result_details.ferry.ferry_operator.name == "Stena Line"
    assert result_details.ferry.duration_in_minutes == 390
    assert result_details.ferry.outbound_segment is True
    assert result_details.ferry.segment_sequence == 1

    result_details = offers[1].result_details[0]
    assert result_details.ferry.duration_in_minutes == 570


async def test_round_trip_initial_search(  # noqa: WPS218
    generator: searches.SearchResultGenerator,
    mock_round_trip_search: models_pb2.Search,
    mock_round_trip_response: None,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(mock_round_trip_search)
    quotes = generator.generate(search_criteria[0])
    offers = [quote async for quote in quotes]

    assert len(offers) == 2

    offer = offers[0].offers[0]
    assert offer.price.units == 104
    assert len(offers[0].result_details) == 1

    result_details = offers[0].result_details[0]
    assert result_details.ferry.origin.ref == "NLMDK"
    assert result_details.ferry.destination.ref == "GBHRW"
    assert result_details.ferry.ferry_operator.name == "Stena Line"
    assert result_details.ferry.duration_in_minutes == 390
    assert result_details.ferry.outbound_segment is True
    assert result_details.ferry.segment_sequence == 1

    result_details = offers[1].result_details[0]
    assert result_details.ferry.duration_in_minutes == 570


async def test_round_trip_return_search(  # noqa: WPS218
    generator: searches.SearchResultGenerator,
    mock_round_trip_search: models_pb2.Search,
    mock_round_trip_response: None,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(mock_round_trip_search)
    quotes = generator.generate(search_criteria[0])
    initial_offers = [quote async for quote in quotes]

    assert len(initial_offers) == 2

    offer = initial_offers[0].offers[0]
    assert offer.price.units == 104
    assert len(initial_offers[0].result_details) == 1

    result_details = initial_offers[0].result_details[0]
    assert result_details.ferry.origin.ref == "NLMDK"
    assert result_details.ferry.destination.ref == "GBHRW"
    assert result_details.ferry.ferry_operator.name == "Stena Line"
    assert result_details.ferry.duration_in_minutes == 390
    assert result_details.ferry.outbound_segment is True
    assert result_details.ferry.segment_sequence == 1

    result_details = initial_offers[1].result_details[0]
    assert result_details.ferry.duration_in_minutes == 570

    mock_round_trip_search.ferry.outbound_offer_id = initial_offers[0].offers[0].id
    return_search_criteria = criteria_generator.criteria_task_generator(
        mock_round_trip_search,
    )
    return_quotes = generator.generate(return_search_criteria[0])
    return_offers = [return_quote async for return_quote in return_quotes]

    assert len(return_offers) == 2

    offer = return_offers[0].offers[0]
    assert offer.price.units == 104

    assert len(return_offers[0].result_details) == 2

    result_details = return_offers[0].result_details[-1]
    assert result_details.ferry.origin.ref == "GBHRW"
    assert result_details.ferry.destination.ref == "NLMDK"
    assert result_details.ferry.ferry_operator.name == "Stena Line"
    assert result_details.ferry.duration_in_minutes == 435
    assert result_details.ferry.outbound_segment is False
    assert result_details.ferry.segment_sequence == 2

    result_details = return_offers[1].result_details[-1]
    assert result_details.ferry.duration_in_minutes == 480


async def test_criteria_generator(  # noqa: WPS218
    generator: searches.SearchResultGenerator,
    mock_round_trip_search: models_pb2.Search,
    criteria_generator: searches.CriteriaGenerator,
) -> None:
    search_criteria = criteria_generator.criteria_task_generator(mock_round_trip_search)

    assert search_criteria[0].origin.ref == "NLMDK"
    assert search_criteria[0].destination.ref == "GBHRW"
    assert search_criteria[0].outbound_departure_datetime == datetime.datetime(  # noqa: DTZ001
        2024,
        4,
        15,
        7,
        0,
    )
    assert search_criteria[0].inbound_departure_datetime == datetime.datetime(  # noqa: DTZ001
        2024,
        4,
        17,
        6,
        0,
    )
    assert search_criteria[0].vehicles == [2]
