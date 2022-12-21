import json
import logging
import secrets
import string

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_ids_and_offer_options_ids,
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def return_randomized_token() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for ii in range(32))


@pytest.mark.integration
async def test_create_offer_quote(
    junction_client: JunctionClient,
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

    offer_ids_and_offer_options_ids = await return_offer_ids_and_offer_options_ids(
        junction_client,
        offer_id_and_offer_group_ids,
    )

    logging.info("offer_ids_and_offer_options_ids: %s", offer_ids_and_offer_options_ids)

    for offer_id_and_offer_option_ids in offer_ids_and_offer_options_ids:
        response_post = await junction_client.create_offer_quote(
            offer_id=offer_id_and_offer_option_ids[0],
            option_ids=[offer_id_and_offer_option_ids[1][0]],
            session_token=return_randomized_token(),
        )

    logging.info("create_offer_quote: %s", json.dumps(response_post, indent=4))
    assert is_valid_uuid(response_post["data"]["id"]) is True
