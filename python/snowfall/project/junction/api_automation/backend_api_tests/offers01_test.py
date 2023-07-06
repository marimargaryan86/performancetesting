import asyncio
import datetime
import json
import logging
from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.junction.go.client import Client, LegType

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_trip_offers_e2e_basic(
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

    assert offer_options_ids, "offer_options_ids should not be empty"


async def return_offer_options_ids_from_offer_searches(
    junction_client: Client,
    offer_id_and_offer_group_ids: Sequence[tuple[Any, ...]],
) -> Sequence[str]:
    offer_options_ids = []
    for idx, _ in enumerate(offer_id_and_offer_group_ids):
        single_item = offer_id_and_offer_group_ids[idx]
        if single_item != ("None", ["None"]):
            offer_group_ids = single_item[1]
            offer_options_ids.extend(
                await return_offer_options_ids(
                    junction_client,
                    offer_group_ids,
                ),
            )
    return offer_options_ids


async def return_offer_ids_and_offer_options_ids(
    client: Client,
    offer_id_and_offer_group_ids: Sequence[tuple[Any, ...]],
) -> Sequence[list[str]]:
    list_of_offer_ids_and_offer_options_ids = []
    for idx, _ in enumerate(offer_id_and_offer_group_ids):
        single_item = offer_id_and_offer_group_ids[idx]
        if single_item != ("None", ["None"]):
            offer_group_ids = single_item[1]
            offer_options_ids = await return_offer_options_ids(
                client,
                offer_group_ids,
            )
            list_of_offer_ids_and_offer_options_ids.append(
                [single_item[0], offer_options_ids],
            )
    return list_of_offer_ids_and_offer_options_ids


async def return_offer_searches_id_and_offer_group_ids(
    junction_client: Client,
    trip_offer_search_ids: Sequence[str],
) -> Sequence[tuple[Any, ...]]:
    tasks = [
        asyncio.create_task(
            return_offer_group_ids_and_offer_searches_id(
                junction_client,
                trip_offer_search_id,
            ),
        )
        for trip_offer_search_id in trip_offer_search_ids
    ]
    offer_id_and_offer_group_ids = await asyncio.gather(*tasks)
    offer_id_and_offer_group_ids = list(filter(bool, offer_id_and_offer_group_ids))
    logging.info(
        "(offer_id, [offer_group_ids]): %s",
        json.dumps(offer_id_and_offer_group_ids, indent=4),
    )
    return offer_id_and_offer_group_ids


async def return_offer_ids(
    junction_client: Client,
    trip_offer_search_ids: Sequence[str],
) -> Sequence[str]:
    tasks = [
        asyncio.create_task(
            return_offer_id(
                junction_client,
                trip_offer_search_id,
            ),
        )
        for trip_offer_search_id in trip_offer_search_ids
    ]
    offer_ids = await asyncio.gather(*tasks)
    logging.info(
        "offer_ids: %s",
        json.dumps(offer_ids, indent=4),
    )
    return offer_ids


async def return_offer_options_details_ids(
    junction_client: Client,
    offer_options_ids: Sequence[str],
) -> Sequence[str]:
    offer_options_details_ids = []
    for offer_options_id in offer_options_ids:
        response = await junction_client.get_offer_option_details_by_offer_option_id(
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
    junction_client: Client,
    trip_offer_search_id: str,
) -> tuple[str, Sequence[str]] | None:
    r1 = await return_offer_search_id_and_offer_group_ids(
        junction_client,
        trip_offer_search_id,
    )
    if r1:
        logging.info("offer_id: %s, offer_group_ids: %s", *r1)
    return r1


async def return_offer_id(
    junction_client: Client,
    trips_search_id: str,
) -> str:
    attempts = 5
    for i0 in range(attempts):
        await asyncio.sleep(2)
        response = await junction_client.get_offers_by_offer_search_id(
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
    junction_client: Client,
    trips_search_id: str,
) -> tuple[str, Sequence[str]] | None:
    response = await junction_client.get_offers_by_offer_search_id(
        trips_search_id,
        cabin_class=["economy"],
    )
    logging.info("get_offers_by_offer_search_id: %s", json.dumps(response, indent=4))

    offer_id = response["data"][0]["id"]
    assert offer_id is not None, "Offer ID is None"

    logging.info("offer_searches_id: %s", offer_id)

    offer_group_ids = await return_offer_group_ids_from_response(response)

    return offer_id, offer_group_ids


async def return_offer_group_ids_from_response(
    response: Mapping[str, Any],
) -> Sequence[str]:
    groups = response["data"][0]["relationships"]["groups"]
    groups_data = groups["data"]
    offer_group_ids = [i1["id"] for i1 in groups_data]
    logging.info("offer_group_ids: %s", offer_group_ids)

    return offer_group_ids


async def return_trip_offer_search_ids(
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> Sequence[str]:
    trip_ids = await get_trip_ids(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    trip_offer_search_ids = []
    for trip_id in trip_ids:
        trip_offer_search_id = await return_trip_offer_search_id(
            junction_client,
            [trip_id],
            1992,
            4,
            29,
        )
        trip_offer_search_ids.append(trip_offer_search_id)

    return await return_final_trip_offer_search_ids(
        junction_client,
        trip_offer_search_ids,
    )


async def return_final_trip_offer_search_ids(
    client: Client,
    trip_offer_search_ids: Sequence[str],
) -> Sequence[str]:
    tasks = [
        asyncio.create_task(
            return_offer_searches_ids_final_values(
                client,
                trip_offer_search_id,
            ),
        )
        for trip_offer_search_id in trip_offer_search_ids
    ]
    final_trip_offer_search_ids = await asyncio.gather(*tasks)
    logging.info(
        "final_trip_offer_search_ids: %s",
        json.dumps(final_trip_offer_search_ids, indent=4),
    )
    filtered_trip_offer_search_ids = await filter_sequence_for_ending_string(
        final_trip_offer_search_ids,
        "_completed",
    )
    logging.info(
        "filtered_trip_offer_search_ids: %s",
        json.dumps(filtered_trip_offer_search_ids, indent=4),
    )

    return filtered_trip_offer_search_ids


async def filter_sequence_for_ending_string(
    final_trip_offer_search_ids: Sequence[str],
    string_to_check: str,
) -> Sequence[str]:
    filtered_trip_offer_search_ids = [
        final_trip_offer_search_id
        for final_trip_offer_search_id in final_trip_offer_search_ids
        if final_trip_offer_search_id.endswith(string_to_check)
    ]

    return [
        filtered_trip_offer_search_id.removesuffix(
            string_to_check,
        )
        for filtered_trip_offer_search_id in filtered_trip_offer_search_ids
    ]


async def return_offer_searches_ids_final_values(
    client: Client,
    trip_offer_search_id: str,
) -> Sequence[str]:
    response = {}
    safety_counter = 0
    do_condition = True
    max_safety_counter = 150
    while do_condition and safety_counter < max_safety_counter:
        response = await client.get_offer_search(trip_offer_search_id)
        logging.info("get_offer_search: %s", json.dumps(response, indent=4))
        status = response["data"]["attributes"]["status"]
        if status in {"completed", "failed", "unspecified"}:
            return "{0}_{1}".format(response["data"]["id"], status)
        if status in {"pending", "processing"}:
            if safety_counter == (max_safety_counter - 1):
                return "{0}_{1}".format(response["data"]["id"], status)
        else:
            await asyncio.sleep(2)
            do_condition = False
            safety_counter += 1

    return response["data"]["id"]


async def return_trip_search_id(
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    trip_id = await get_trip_id(
        junction_client,
        departure_after,
        destination,
        origin,
    )
    logging.info("trip_id: %s", json.dumps(trip_id, indent=4))

    return await return_trip_search_id_from_trip_id(
        junction_client,
        trip_id,
        year=1992,
        month=4,
        day=29,
    )


async def return_offer_group_details(
    junction_client: Client,
    offer_group_ids: Sequence[str],
) -> list[str]:
    offer_group_details_ids = []
    for offer_groups_id in offer_group_ids:
        response = await junction_client.get_offer_group_details_by_offer_group_id(
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
    junction_client: Client,
    offer_group_ids: Sequence[str],
) -> list[str]:
    offer_options_ids = []
    for offer_groups_id in offer_group_ids:
        r6 = await junction_client.get_offer_options_by_offer_group_id(
            offer_groups_id,
        )
        for idx, _ in enumerate(r6["data"]):
            offer_options_ids.append(r6["data"][idx]["id"])

    logging.info("offer_options_ids: %s", json.dumps(offer_options_ids, indent=4))

    return offer_options_ids


async def return_trip_offer_search_id(
    junction_client: Client,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> str:
    r3 = await junction_client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))
    offer_search_id = r3["data"]["id"]
    for _ in range(3):
        await asyncio.sleep(1000)
        resp = await junction_client.get_offer_search(offers_search_id=offer_search_id)
        if resp["data"]["attributes"] == "completed":
            break
    else:
        raise RuntimeError("Offer search status check was timed out!")
    return offer_search_id


async def return_trip_search_id_from_trip_id(
    junction_client: Client,
    trip_id: str,
    year: int,
    month: int,
    day: int,
) -> str:
    r3 = await junction_client.create_offer_search(
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
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> list[str]:
    r1 = await return_trip_search_final_response(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    logging.info("create_trip_search: %s", json.dumps(r1, indent=4))
    trip_search_id = r1["data"]["id"]
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    r2 = await junction_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id: %s", json.dumps(r2, indent=4))

    trip_ids = [trip["id"] for trip in r2["data"]]
    logging.info("trip_ids: %s", trip_ids)

    return trip_ids


async def get_trip_id(
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> str:
    r1 = await return_trip_search_final_response(
        junction_client,
        departure_after,
        destination,
        origin,
    )

    logging.info("create_trip_search: %s", json.dumps(r1, indent=4))
    trip_search_id = r1["data"]["id"]
    assert is_valid_uuid(trip_search_id) is True, "trip_search_id uuid in v4 format"

    r2 = await junction_client.trips().get_trips_by_trip_search_id(trip_search_id)
    logging.info("get_trips_by_trip_search_id: %s", json.dumps(r2, indent=4))

    assert r2["data"], "No trips were found"
    trip_id = r2["data"][0]["id"]
    logging.info("trip_id: %s", trip_id)
    assert is_valid_uuid(trip_id, 5) is True, "trip_id uuid must be in uuid v5 format"

    return trip_id


async def return_trip_search_final_response(
    junction_client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> dict[str, Any]:
    do_condition = True
    safety_counter = 0
    response = await junction_client.trips().create_trip_search(
        origin_id=origin,
        destination_id=destination,
        departure_after=datetime.datetime.fromisoformat(
            departure_after[:-1],
        ).astimezone(datetime.UTC),
        allowed_segment_types=[LegType.air],
    )
    logging.info("trips().create_trip_search: %s", json.dumps(response, indent=4))
    status = response["data"]["attributes"]["status"]
    while do_condition and safety_counter < 30:
        logging.info("trip_search status: %s", status)
        if status in {"completed", "unspecified", "failed"}:
            do_condition = False
        else:
            await asyncio.sleep(2)
            r1 = await junction_client.trips().get_trip_search_by_id(
                response["data"]["id"],
            )
            status = r1["data"]["attributes"]["status"]
            safety_counter += 1
    return response
