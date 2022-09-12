import datetime
import logging
import time
from pprint import pformat
from typing import Any, Mapping, Sequence, Tuple

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.client import JunctionClient, LegType

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_trip_offers_e2e_basic(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    (
        offer_group_ids,
        offer_searches_id,
    ) = await return_offer_group_ids_and_offer_searches_id(
        client,
        departure_after,
        destination,
        origin,
    )

    assert offer_searches_id is not None, "offer_searches_id should not be empty"
    assert offer_group_ids is not None, "offer_group_ids should not be empty"
    time.sleep(20)

    # list offer options by offer group
    offer_options_ids = await return_offer_options_ids(
        client,
        offer_group_ids,
    )
    assert offer_options_ids is not None, "offer_options_ids should not be empty"


@pytest.mark.integration
async def test_get_offer_group_details_by_offer_group_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    (
        offer_group_ids,
        offer_searches_id,
    ) = await return_offer_group_ids_and_offer_searches_id(
        client,
        departure_after,
        destination,
        origin,
    )

    assert offer_searches_id is not None, "offer_searches_id should not be empty"
    assert offer_group_ids is not None, "offer_group_ids should not be empty"
    time.sleep(20)

    offer_group_details_id = await return_offer_group_details(
        client,
        offer_group_ids,
    )
    assert (
        offer_group_details_id is not None
    ), "offer_group_details_id should not be empty"


@pytest.mark.integration
async def test_get_offer_option_details_by_offer_option_id(
    host: str,
    api_token: str,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    client = JunctionClient(api_url="https://{0}".format(host), token=api_token)

    (
        offer_group_ids,
        offer_searches_id,
    ) = await return_offer_group_ids_and_offer_searches_id(
        client,
        departure_after,
        destination,
        origin,
    )

    assert offer_searches_id is not None, "offer_searches_id should not be empty"
    assert offer_group_ids is not None, "offer_group_ids should not be empty"
    time.sleep(20)

    offer_options_ids = await return_offer_options_ids(
        client,
        offer_group_ids,
    )
    assert offer_options_ids is not None, "offer_options_ids should not be empty"

    offer_options_details_ids = await return_offer_options_details_ids(
        client,
        offer_options_ids,
    )

    assert (
        offer_options_details_ids is not None
    ), "offer_options_ids should not be empty"


async def return_offer_options_details_ids(
    client: JunctionClient,
    offer_options_ids: Sequence[str],
) -> Sequence[str]:
    offer_options_details_ids = []
    for offer_options_id in offer_options_ids:
        response = await client.get_offer_option_details_by_offer_option_id(
            offer_options_id,
        )
        logging.info(
            "get_offer_option_details_by_offer_option_id %s",
            pformat(response),
        )
        offer_options_details_ids.append(response["data"][0]["id"])
    logging.info("offer_options_details_ids: %s", offer_options_details_ids)

    return offer_options_details_ids


async def return_offer_group_ids_and_offer_searches_id(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> Tuple[str, Sequence[str]]:
    trips_search_id = await return_trip_search_id(
        client,
        departure_after,
        destination,
        origin,
    )
    attempts = 30
    for i0 in range(attempts):
        time.sleep(2)
        (
            offer_searches_id,
            offer_group_ids,
        ) = await return_offer_search_id_and_offer_group_ids(
            client,
            trips_search_id,
        )
        logging.info(
            "Iteration: %s of %s: offer_searches_id: %s, offer_group_ids: %s",
            i0,
            attempts,
            offer_searches_id,
            offer_group_ids,
        )
        if offer_searches_id is None or offer_group_ids == ["None"]:
            logging.info("Checking again")
        else:
            break

    return offer_searches_id, offer_group_ids


async def return_offer_search_id_and_offer_group_ids(
    client: JunctionClient,
    trips_search_id: str,
) -> Tuple[str, Sequence[str]]:
    response = await client.get_offers_by_offer_search_id(
        trips_search_id,
        cabin_class=["economy"],
    )
    logging.info("get_offers_by_offer_search_id: %s", pformat(response))

    try:
        offer_searches_id = response["data"][0]["id"]
    except IndexError:
        logging.info("offer_searches_id is empty")
        return "None", ["None"]
    logging.info("offer_searches_id: %s", offer_searches_id)

    offer_group_ids = await return_offer_group_ids_from_response(response)

    return offer_searches_id, offer_group_ids


async def return_offer_group_ids_from_response(
    response: Mapping[str, Any],
) -> Sequence[str]:
    offer_group_ids = []
    groups = response["data"][0]["relationships"]["groups"]
    groups_data = groups["data"]
    for i1 in groups_data:
        offer_group_ids.append(i1["id"])
    logging.info("offer_group_ids: %s", offer_group_ids)

    return offer_group_ids


async def return_trip_search_id(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    trip_id = await get_trip_id(
        client,
        departure_after,
        destination,
        origin,
    )
    time.sleep(5)
    logging.info("trip_id: %s", pformat(trip_id))

    return await return_trips_search_id(
        client,
        trip_id,
        year=1992,
        month=4,
        day=29,
    )


async def return_offer_group_details(
    client: JunctionClient,
    offer_group_ids: Sequence[str],
) -> list[str]:
    offer_group_details_id = []
    for offer_groups_id in offer_group_ids:
        response = await client.get_offer_group_details_by_offer_group_id(
            offer_groups_id,
        )
        logging.info("get_offer_group_details_by_offer_group_id: %s", pformat(response))
        offer_group_details_id.append(response["data"][0]["id"])
    logging.info("offer_group_details_id: %s", pformat(offer_group_details_id))

    return offer_group_details_id


async def return_offer_options_ids(
    client: JunctionClient,
    offer_group_ids: Sequence[str],
) -> list[str]:
    offer_options_ids = []
    for offer_groups_id in offer_group_ids:
        r6 = await client.get_offer_options_by_offer_group_id(
            offer_groups_id,
        )
        offer_options_ids.append(r6["data"][0]["id"])
    logging.info("offer_options_ids: %s", pformat(offer_options_ids))

    return offer_options_ids


async def return_trips_search_id(
    client: JunctionClient,
    trip_id: str,
    year: int,
    month: int,
    day: int,
) -> str:
    r3 = await client.create_offer_search(
        trip_ids=[trip_id],
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", pformat(r3))

    return r3["data"]["id"]


async def get_trip_id(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    r1 = await client.create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(datetime.timezone.utc),
        leg_types=[LegType.air],
    )
    logging.info("create_trip_search: %s", pformat(r1))
    trip_search_id = r1["data"]["id"]
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    time.sleep(5)

    r2 = await client.get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id: %s", pformat(r2))

    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    return trip_id
