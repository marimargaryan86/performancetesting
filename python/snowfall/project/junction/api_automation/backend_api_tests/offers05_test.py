import json
import logging
from typing import Any, Sequence, Tuple

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    return_offer_searches_id_and_offer_group_ids,
    return_trip_offer_search_ids,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_offer_groups_by_offer_group_id(
    junction_client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    offer_id_and_offer_group_ids = await return_offer_searches_id_and_offer_group_ids(
        junction_client,
        await return_trip_offer_search_ids(
            junction_client,
            departure_after,
            destination,
            origin,
        ),
    )
    logging.info("offer_id_and_offer_group_ids: %s", offer_id_and_offer_group_ids)
    clean_offer_id_and_offer_group_ids = await clean_empty_items(
        offer_id_and_offer_group_ids,
    )
    logging.info(
        "clean_offer_id_and_offer_group_ids: %s",
        clean_offer_id_and_offer_group_ids,
    )

    responses = await return_flat_responses_get_offer_groups_by_offer_group_id(
        clean_offer_id_and_offer_group_ids,
        junction_client,
    )
    for response in responses:
        assert response is not None


async def return_flat_responses_get_offer_groups_by_offer_group_id(
    clean_offer_id_and_offer_group_ids: Sequence[Tuple[Any, ...]],
    junction_client: JunctionClient,
) -> Sequence[dict[str, Any]]:
    responses = []
    for clean_offer_id_and_offer_group_id in clean_offer_id_and_offer_group_ids:
        responses.append(
            await responses_get_offer_groups_by_offer_group_id(
                clean_offer_id_and_offer_group_id,
                junction_client,
            ),
        )

    return [data_item for sublist in responses for data_item in sublist]


async def responses_get_offer_groups_by_offer_group_id(
    clean_offer_id_and_offer_group_id: Tuple[Any, ...],
    junction_client: JunctionClient,
) -> Sequence[dict[str, Any]]:
    responses = []
    for idx, offer_group_ids in enumerate(clean_offer_id_and_offer_group_id):
        if idx != 0:
            for offer_group_id in offer_group_ids:
                response = await junction_client.get_offer_groups_by_offer_group_id(
                    offer_group_id,
                )
                logging.info(
                    "get_offer_groups_by_offer_group_id:  %s",
                    json.dumps(response, indent=4),
                )
                responses.append(response)

    return responses


async def return_nonempty_offer_ids_and_offer_group_ids(
    junction_client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> Sequence[Tuple[Any, ...]]:
    offer_id_and_offer_group_ids = await return_offer_searches_id_and_offer_group_ids(
        junction_client,
        await return_trip_offer_search_ids(
            junction_client,
            departure_after,
            destination,
            origin,
        ),
    )
    logging.info("offer_id_and_offer_group_ids: %s", offer_id_and_offer_group_ids)
    clean_offer_id_and_offer_group_ids = await clean_empty_items(
        offer_id_and_offer_group_ids,
    )
    logging.info(
        "clean_offer_id_and_offer_group_ids: %s",
        clean_offer_id_and_offer_group_ids,
    )
    return clean_offer_id_and_offer_group_ids


async def clean_empty_items(
    offer_id_and_offer_group_ids: Sequence[Tuple[Any, ...]],
) -> list[tuple[Any, ...]]:
    nonempty_offer_id_and_offer_group_ids = []
    for idx, _ in enumerate(offer_id_and_offer_group_ids):
        single_item = offer_id_and_offer_group_ids[idx]
        if single_item != ("None", ["None"]):
            nonempty_offer_id_and_offer_group_ids.append(single_item)

    return nonempty_offer_id_and_offer_group_ids
