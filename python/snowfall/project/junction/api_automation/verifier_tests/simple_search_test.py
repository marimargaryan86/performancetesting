import logging
from collections.abc import Sequence
from datetime import date, datetime

import pytest

from snowfall.project.junction.api_automation.mobile_api_tests.e2e_simple_search_test import (
    create_offer_simple_search,
    get_offer_list_simple_search,
    get_option_id,
    get_place_coordinates,
    get_search_offers,
)
from snowfall.project.junction.api_automation.test_functions.helper import (
    wait_until_completed,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)
from snowfall.vendor.junction.go.client import LegType

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

places_pairs = [("Brussels-Midi", "Rotterdam Centraal")]
providers = [
    "Custom",
]


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.verify()
@pytest.mark.parametrize("places_pairs", places_pairs, ids=providers)
async def test_verify_simple_search(  # noqa: WPS218
    mock_mobile_client: MobileApiClient,
    places_pairs: Sequence[str],
    departure_after: datetime,
) -> None:
    origin_cord, destination_cord = await get_place_coordinates(
        mock_mobile_client,
        places_pairs,
    )
    assert origin_cord, "Origin not found"
    assert destination_cord, "Destination not found"
    logger.info("Get Origin and Destination step: SUCCEED")
    offer_simple_search = await create_offer_simple_search(
        mock_mobile_client,
        departure_after,
        origin_cord,
        destination_cord,
        [date(1980, 2, 3)],
        maximum_connections=2,
        allowed_segment_types=[LegType.rail],
    )
    offer_id_simple_search = offer_simple_search["data"]["id"]
    assert offer_id_simple_search, "offer is with simpl search wasn't found"
    logger.info("Create Simple Offers Search step: SUCCEED")

    offer_search_data = await wait_until_completed(
        lambda: get_search_offers(mock_mobile_client, offer_id_simple_search),
        "Timeout reached and status was not completed.",
    )
    assert offer_search_data
    logger.info("Get Simple Offers Search step: SUCCEED")

    offers_list = await get_offer_list_simple_search(
        mock_mobile_client,
        offer_id_simple_search,
    )
    assert "included" in offers_list, "no offers"
    offer_included = offers_list["included"]
    assert offer_included
    offer_id = offers_list["data"][0]["id"]
    offer_option_id = await get_option_id(offer_id, offers_list)
    assert offer_id
    assert offer_option_id
    logger.info("Get Offer ID and Option ID step: SUCCEED")
