import logging

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_group_details,
    return_offer_group_ids_and_offer_searches_id,
    return_trip_search_id,
)
from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_offer_group_details_by_offer_group_id(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trips_search_id = await return_trip_search_id(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    (
        offer_searches_id,
        offer_group_ids,
    ) = await return_offer_group_ids_and_offer_searches_id(
        junction_client,
        trips_search_id,
    )

    assert trips_search_id is not None, "no data"
    assert offer_searches_id is not None, "offer_searches_id should not be empty"
    assert offer_group_ids is not None, "offer_group_ids should not be empty"

    offer_group_details_ids = await return_offer_group_details(
        junction_client,
        offer_group_ids,
    )
    assert (
        offer_group_details_ids is not None
    ), "offer_group_details_ids should not be empty"
