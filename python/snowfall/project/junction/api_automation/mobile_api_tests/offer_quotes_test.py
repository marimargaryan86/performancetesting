import json
import logging
from typing import Any

import pytest

from snowfall.project.junction.api_automation.mobile_api_tests.trip_candidate_search_test import (
    create_trip_candidate_search,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def list_trips_candidates_offers(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> dict[str, Any]:
    candidate_search = await create_trip_candidate_search(
        mobile_client,
        departure_after,
    )
    offers_response = await mobile_client.list_trip_candidates_offers(candidate_search)
    logger.info("list_candidates_offers: %s", json.dumps(offers_response, indent=4))

    return offers_response


@pytest.mark.integration()
async def test_create_offer_quote(
    mobile_client: MobileApiClient,
    departure_after: str,
) -> None:
    offers_response = await list_trips_candidates_offers(
        mobile_client,
        departure_after,
    )
    options = offers_response["included"][0]["relationships"]["options"]
    options_id = options["data"][0]["id"]
    offer_price_quote = await mobile_client.create_offer_price_quote(
        offer_id=offers_response["data"][0]["id"],
        options_id=options_id,
    )
    logger.info("create_offer_price_quote: %s", json.dumps(offer_price_quote, indent=4))
    quote_id = offer_price_quote["data"]["id"]
    assert quote_id is not None
