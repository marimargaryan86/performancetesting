import asyncio
import datetime
import json
import logging
import time
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
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_offer_search_ids = await return_trip_offer_search_ids(
        client,
        departure_after,
        destination,
        origin,
    )

    offer_id_and_offer_group_ids = await return_offer_searches_id_and_offer_group_ids(
        client,
        trip_offer_search_ids,
    )

    offer_options_ids = await return_offer_options_ids_from_offer_searches(
        client,
        offer_id_and_offer_group_ids,
    )

    assert offer_options_ids, "offer_options_ids should not be empty"


async def return_offer_options_ids_from_offer_searches(
    client: JunctionClient,
    offer_id_and_offer_group_ids: Sequence[Tuple[Any, ...]],
) -> Sequence[str]:
    offer_options_ids = []
    for idx, _ in enumerate(offer_id_and_offer_group_ids):
        single_item = offer_id_and_offer_group_ids[idx]
        if single_item != ("None", ["None"]):
            offer_group_ids = single_item[1]
            offer_options_ids.extend(
                await return_offer_options_ids(
                    client,
                    offer_group_ids,
                ),
            )
    return offer_options_ids


async def return_offer_searches_id_and_offer_group_ids(
    client: JunctionClient,
    trip_offer_search_ids: Sequence[str],
) -> Sequence[Tuple[Any, ...]]:
    tasks = []
    for trip_offer_search_id in trip_offer_search_ids:
        tasks.append(
            asyncio.create_task(
                return_offer_group_ids_and_offer_searches_id(
                    client,
                    trip_offer_search_id,
                ),
            ),
        )
    offer_id_and_offer_group_ids = await asyncio.gather(*tasks)
    logging.info(
        "(offer_id, [offer_group_ids]): %s",
        json.dumps(offer_id_and_offer_group_ids, indent=4),
    )
    return offer_id_and_offer_group_ids


async def return_offer_ids(
    client: JunctionClient,
    trip_offer_search_ids: Sequence[str],
) -> Sequence[str]:
    tasks = []
    for trip_offer_search_id in trip_offer_search_ids:
        tasks.append(
            asyncio.create_task(
                return_offer_id(
                    client,
                    trip_offer_search_id,
                ),
            ),
        )
    offer_ids = await asyncio.gather(*tasks)
    logging.info(
        "offer_ids: %s",
        json.dumps(offer_ids, indent=4),
    )
    return offer_ids


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
            json.dumps(response, indent=4),
        )
        offer_options_details_ids.append(response["data"][0]["id"])
    logging.info("offer_options_details_ids: %s", offer_options_details_ids)

    return offer_options_details_ids


async def return_offer_group_ids_and_offer_searches_id(
    client: JunctionClient,
    trip_offer_search_id: str,
) -> Tuple[str, Sequence[str]]:
    attempts = 25
    for i0 in range(attempts):
        time.sleep(2)
        (offer_id, offer_group_ids) = await return_offer_search_id_and_offer_group_ids(
            client,
            trip_offer_search_id,
        )
        if not (offer_id is None or offer_group_ids == ["None"]):
            logging.info(
                "Iteration: %s of %s: offer_id: %s, offer_group_ids: %s",
                i0,
                attempts,
                offer_id,
                offer_group_ids,
            )
            break

    return offer_id, offer_group_ids


async def return_offer_id(
    client: JunctionClient,
    trips_search_id: str,
) -> str:
    attempts = 5
    for i0 in range(attempts):
        time.sleep(2)
        response = await client.get_offers_by_offer_search_id(
            trips_search_id,
            cabin_class=["economy"],
        )
        logging.info(
            "get_offers_by_offer_search_id: %s",
            json.dumps(response, indent=4),
        )
        if response["data"][0]["id"] is not None:
            logging.info(
                "Iteration: %s of %s: offer_id: %s",
                i0,
                attempts,
                response["data"]["id"],
            )
            break

    return response["data"][0]["id"]


async def return_offer_search_id_and_offer_group_ids(
    client: JunctionClient,
    trips_search_id: str,
) -> Tuple[str, Sequence[str]]:
    response = await client.get_offers_by_offer_search_id(
        trips_search_id,
        cabin_class=["economy"],
    )
    logging.info("get_offers_by_offer_search_id: %s", json.dumps(response, indent=4))

    try:
        offer_id = response["data"][0]["id"]
    except IndexError:
        return "None", ["None"]
    logging.info("offer_searches_id: %s", offer_id)

    offer_group_ids = await return_offer_group_ids_from_response(response)

    return offer_id, offer_group_ids


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


async def return_trip_offer_search_ids(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> Sequence[str]:
    trip_ids = await get_trip_ids(
        client,
        departure_after,
        destination,
        origin,
    )
    time.sleep(10)

    trip_offer_search_ids = []
    for trip_id in trip_ids:
        trip_offer_search_id = await return_trip_offer_search_id(
            client,
            [trip_id],
            1992,
            4,
            29,
        )
        trip_offer_search_ids.append(trip_offer_search_id)

    return trip_offer_search_ids


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
    time.sleep(10)
    logging.info("trip_id: %s", json.dumps(trip_id, indent=4))

    return await return_trip_search_id_from_trip_id(
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
    offer_group_details_ids = []
    for offer_groups_id in offer_group_ids:
        response = await client.get_offer_group_details_by_offer_group_id(
            offer_groups_id,
        )
        logging.info(
            "get_offer_group_details_by_offer_group_id: %s",
            json.dumps(response, indent=4),
        )
        offer_group_details_ids.append(response["data"][0]["id"])
    logging.info(
        "offer_group_details_ids: %s",
        json.dumps(offer_group_details_ids, indent=4),
    )

    return offer_group_details_ids


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
    logging.info("offer_options_ids: %s", json.dumps(offer_options_ids, indent=4))

    return offer_options_ids


async def return_trip_offer_search_id(
    client: JunctionClient,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> str:
    r3 = await client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))

    return r3["data"]["id"]


async def return_trip_search_id_from_trip_id(
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
    logging.info(
        "create_offer_search: %s for trip_id %s",
        json.dumps(r3, indent=4),
        trip_id,
    )

    return r3["data"]["id"]


async def get_trip_ids(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> list[str]:
    r1 = await client.trips().create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(datetime.timezone.utc),
        leg_types=[LegType.air],
    )
    logging.info("create_trip_search: %s", json.dumps(r1, indent=4))
    trip_search_id = r1["data"]["id"]
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    time.sleep(15)

    r2 = await client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id: %s", json.dumps(r2, indent=4))

    trip_ids = []
    for idx, _ in enumerate(r2["data"]):
        trip_ids.append(r2["data"][idx]["id"])
    logging.info("trip_ids: %s", trip_ids)

    return trip_ids


async def get_trip_id(
    client: JunctionClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    r1 = await client.trips().create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(datetime.timezone.utc),
        leg_types=[LegType.air],
    )
    logging.info("create_trip_search: %s", json.dumps(r1, indent=4))
    trip_search_id = r1["data"]["id"]
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    time.sleep(5)

    r2 = await client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id: %s", json.dumps(r2, indent=4))

    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    return trip_id
