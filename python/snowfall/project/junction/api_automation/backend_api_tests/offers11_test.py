import json
import logging
import time
from typing import Any, Sequence, Tuple

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_ids_and_offer_options_ids,
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_offer_quote_by_id(
    junction_client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    offer_id_and_offer_group_ids = await return_offer_id_and_offer_group_ids(
        departure_after,
        destination,
        junction_client,
        origin,
    )

    offer_ids_and_offer_options_ids = await return_offer_ids_and_offer_options_ids(
        junction_client,
        offer_id_and_offer_group_ids,
    )
    logging.info("offer_ids_and_offer_options_ids: %s", offer_ids_and_offer_options_ids)

    response_post = {}
    for offer_id_and_offer_option_ids in offer_ids_and_offer_options_ids:
        response_post = await junction_client.create_offer_quote(
            offer_id=offer_id_and_offer_option_ids[0],
            option_ids=[offer_id_and_offer_option_ids[1][0]],
            session_token=return_randomized_token(),
        )

        logging.info("create_offer_quote: %s", json.dumps(response_post, indent=4))
        assert is_valid_uuid(response_post["data"]["id"]) is True

    await calculate_time_and_get_price_quote_response(
        junction_client,
        response_post["data"]["id"],
    )


async def calculate_time_and_get_price_quote_response(
    junction_client: JunctionClient,
    trip_offer_price_quote_id: str,
) -> None:
    st = time.time()
    response = await return_get_price_offer_quote_final_values(
        junction_client,
        trip_offer_price_quote_id,
    )
    et = time.time()
    elapsed_time = et - st
    logging.info("return_get_price_offer_quote_final_values: %s", response)
    logging.info(
        "return_get_price_offer_quote_final_values time elapsed: %s",
        elapsed_time,
    )


async def return_offer_id_and_offer_group_ids(
    departure_after: str,
    destination: str,
    junction_client: JunctionClient,
    origin: str,
) -> Sequence[Tuple[Any, ...]]:
    trip_offer_search_ids = await return_trip_offer_search_ids(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    return await return_offer_searches_id_and_offer_group_ids(
        junction_client,
        trip_offer_search_ids,
    )


async def return_get_price_offer_quote_final_values(
    junction_client: JunctionClient,
    trip_offer_price_quote_id: str,
) -> Sequence[str]:
    response = {}
    safety_counter = 0
    do_condition = True
    max_safety_counter = 150
    while do_condition and safety_counter < max_safety_counter:
        response = await junction_client.get_offer_quote_by_id(
            trip_offer_price_quote_id,
        )
        logging.info("get_offer_quote_by_id: %s", json.dumps(response, indent=4))
        status = response["data"]["attributes"]["status"]
        if status in {"completed", "failed", "unspecified"}:
            return "{0}_{1}".format(response["data"]["id"], status)
        elif status in {"pending", "processing"}:
            if safety_counter == (max_safety_counter - 1):
                return "{0}_{1}".format(response["data"]["id"], status)
        else:
            time.sleep(2)
            do_condition = False
            safety_counter += 1
    return response["data"]["id"]
