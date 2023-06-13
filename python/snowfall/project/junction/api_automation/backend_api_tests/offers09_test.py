import logging

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_options_ids_from_offer_searches,
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import with_log
from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_offer_option_detail_rules(  # noqa: WPS210
    junction_client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_offer_search_ids = await return_trip_offer_search_ids(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    offer_id_and_offer_group_ids = await return_offer_searches_id_and_offer_group_ids(
        junction_client,
        trip_offer_search_ids,
    )

    offer_options_ids = await return_offer_options_ids_from_offer_searches(
        junction_client,
        offer_id_and_offer_group_ids,
    )

    for option_id in offer_options_ids:
        resp = await with_log(
            junction_client.get_offer_option_details_by_offer_option_id,
        )(
            option_id,
        )
        for detail in resp["data"]:
            for rule in detail["attributes"]["rules"]:
                assert "data" in rule
                assert "title" in rule
