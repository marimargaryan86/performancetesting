import json
import logging
from typing import Any, Sequence, Tuple

import pytest

from snowfall.project.junction.api_automation.offers01_test import (
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_offer_search(
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    offer_id_and_offer_group_ids = await return_offer_searches_id_and_offer_group_ids(
        client,
        await return_trip_offer_search_ids(
            client,
            departure_after,
            destination,
            origin,
        ),
    )

    offer_ids = await extract_offer_ids(
        offer_id_and_offer_group_ids,
    )

    logging.info("offer_ids: %s", offer_ids)

    for offer_id in offer_ids:
        response = await client.get_offer(offer_id)
        logging.info("get_offer:  %s", json.dumps(response, indent=4))

        assert offer_id == response["data"]["id"]


async def extract_offer_ids(
    offer_id_and_offer_group_ids: Sequence[Tuple[Any, ...]],
) -> Sequence[str]:
    offer_ids = []
    for idx, _ in enumerate(offer_id_and_offer_group_ids):
        single_item = offer_id_and_offer_group_ids[idx]
        if single_item != ("None", ["None"]):
            offer_ids.append(single_item[0])

    return offer_ids
