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
async def test_get_offer_group_details(
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    offer_group_details_ids = await return_offer_group_details_ids(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    for offer_group_details_id in offer_group_details_ids:
        response = await junction_client.get_offer_group_details(offer_group_details_id)
        logging.info("get_offer_group_details: %s", response)
        assert response is not None


async def return_offer_group_details_ids(
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> list[str]:
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

    return await return_offer_group_details(
        junction_client,
        offer_group_ids,
    )
