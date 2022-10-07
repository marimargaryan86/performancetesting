import logging
from typing import Sequence

import pytest

from snowfall.project.junction.api_automation.offers01_test import (
    return_offer_options_details_ids,
    return_offer_options_ids_from_offer_searches,
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_offer_option_details(
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    offer_options_details_ids = await return_offer_options_details_ids(
        client,
        await return_offer_options_ids(
            client,
            departure_after,
            destination,
            origin,
        ),
    )

    all_responses = []
    for offer_options_details_id in offer_options_details_ids:
        response = await client.get_offer_option_details(
            offer_options_details_id,
        )
        logging.info("get_offer_option_details: %s", response)
        assert response
        all_responses.append(response)

    assert all_responses


async def return_offer_options_ids(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> Sequence[Sequence[str]]:
    trips_offer_search_ids = await return_trip_offer_search_ids(
        client,
        departure_after,
        destination,
        origin,
    )
    offer_searches_id_and_offer_group_ids = (
        await return_offer_searches_id_and_offer_group_ids(
            client,
            trips_offer_search_ids,
        )
    )

    return await return_offer_options_ids_from_offer_searches(
        client,
        offer_searches_id_and_offer_group_ids,
    )
