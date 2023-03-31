import logging

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_options_details_ids,
    return_offer_options_ids_from_offer_searches,
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_offer_option_details_by_offer_option_id(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trips_offer_search_ids = await return_trip_offer_search_ids(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    offer_searches_id_and_offer_group_ids = (
        await return_offer_searches_id_and_offer_group_ids(
            junction_client,
            trips_offer_search_ids,
        )
    )

    offer_options_ids = await return_offer_options_ids_from_offer_searches(
        junction_client,
        offer_searches_id_and_offer_group_ids,
    )
    assert offer_options_ids is not None, "offer_options_ids should not be empty"

    offer_options_details_ids = await return_offer_options_details_ids(
        junction_client,
        offer_options_ids,
    )

    assert (
        offer_options_details_ids is not None
    ), "offer_options_details_ids should not be empty"
