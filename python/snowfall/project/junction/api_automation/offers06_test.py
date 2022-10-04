import logging
import time

import httpx
import pytest

from snowfall.project.junction.api_automation.offers01_test import (
    return_offer_group_details,
    return_offer_group_ids_and_offer_searches_id,
    return_trip_search_id,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_offer_group_details(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=10),
    )

    offer_group_details_ids = await return_offer_group_details_ids(
        client,
        departure_after,
        destination,
        origin,
    )

    for offer_group_details_id in offer_group_details_ids:
        response = await client.get_offer_group_details(offer_group_details_id)
        logging.info("get_offer_group_details: %s", response)
        assert response is not None


async def return_offer_group_details_ids(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> list[str]:
    trips_search_id = await return_trip_search_id(
        client,
        departure_after,
        destination,
        origin,
    )
    (
        offer_searches_id,
        offer_group_ids,
    ) = await return_offer_group_ids_and_offer_searches_id(
        client,
        trips_search_id,
    )
    time.sleep(20)
    return await return_offer_group_details(
        client,
        offer_group_ids,
    )
