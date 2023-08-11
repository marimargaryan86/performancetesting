import asyncio
import csv
import datetime
import json
import logging
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import aiofiles
import allure
import pytest
from aiocsv import writers
from dateutil.parser import parse as datetime_parse

from snowfall.vendor.junction.go.client import Client, LegType

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_trip_windows_planner(
    client: Client,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    trip_ids = await get_trip_ids_with_minimum_segments(
        client,
        departure_after,
        destination,
        origin,
        segments_min_length=1,
        segments_max_length=40,
    )
    short_file_name = "{0}_{1}_{2}_{3}".format(
        "MinimumConnectionTime-calculations",
        origin,
        destination,
        departure_after,
    )
    file_name = Path(tempfile.gettempdir(), short_file_name).with_suffix(".csv")

    await save_mct_to_csv(
        client,
        trip_ids,
        file_name,
    )

    allure.attach.file(
        str(file_name),
        short_file_name,
        allure.attachment_type.CSV,
        extension=csv,
    )


async def save_mct_to_csv(
    client: Client,
    trip_ids: Sequence[str],
    file_name: Path,
) -> None:
    async with aiofiles.open(file_name, "w") as f0:
        writer = writers.AsyncWriter(f0)
        await writer.writerow(
            [
                "trip_id",
                "leg_id",
                "departureAt",
                "arrivalAt",
                "origin",
                "destination",
                "legType",
                "MCT",
            ],
        )
        for trip_id in trip_ids:
            response = await client.legs().get_legs_by_trip_id(trip_id)
            logging.info("get_legs_by_trip_id: %s", json.dumps(response, indent=4))
            all_legs_array = sorted(
                response["data"],
                key=lambda json_key: json_key["attributes"]["departureAt"],
                reverse=False,
            )
            logging.info("all_legs_array %s", json.dumps(all_legs_array, indent=4))
            await extract_data_from_legs_for_trip_id(
                all_legs_array,
                trip_id,
                writer,
            )


async def extract_data_from_legs_for_trip_id(
    all_legs_array: Sequence[Mapping[str, Any]],
    trip_id: str,
    writer: Any,
) -> None:
    for idx, leg_value in enumerate(all_legs_array):
        if idx > 0:
            mct_row = await calculate_mct_row(all_legs_array, idx)
        else:
            mct_row = None
        writer.writerow(
            [
                trip_id,
                leg_value["id"],
                leg_value["attributes"]["departureAt"],
                leg_value["attributes"]["arrivalAt"],
                leg_value["attributes"]["origin"]["ref"],
                leg_value["attributes"]["destination"]["ref"],
                leg_value["relationships"]["legType"]["data"]["id"],
                "segment start" if mct_row is None else mct_row,
            ],
        )


async def calculate_mct_row(
    all_legs_array: Sequence[Mapping[str, Any]],
    idx: int,
) -> datetime.timedelta:
    updated_arrival = await calculate_updated_arrival(all_legs_array, idx)

    updated_departure = await calculate_updated_departure(all_legs_array, idx)

    return updated_departure - updated_arrival


async def calculate_updated_departure(
    all_legs_array: Sequence[Mapping[str, Any]],
    idx: int,
) -> datetime.datetime:
    replace_dd = datetime_parse(
        all_legs_array[idx]["attributes"]["departureAt"],
        ignoretz=False,
    ).replace(
        tzinfo=None,
    )
    utcoffset_dd = datetime_parse(
        all_legs_array[idx]["attributes"]["departureAt"],
    ).utcoffset()

    return replace_dd - utcoffset_dd if utcoffset_dd is not None else replace_dd


async def calculate_updated_arrival(
    all_legs_array: Sequence[Mapping[str, Any]],
    idx: int,
) -> datetime.datetime:
    replace_da = datetime_parse(
        all_legs_array[idx - 1]["attributes"]["arrivalAt"],
        ignoretz=False,
    ).replace(
        tzinfo=None,
    )
    utcoffset_da = datetime_parse(
        all_legs_array[idx - 1]["attributes"]["arrivalAt"],
    ).utcoffset()

    return replace_da - utcoffset_da if utcoffset_da is not None else replace_da


async def get_trip_ids_with_minimum_segments(
    client: Client,
    departure_after: str,
    destination: str,
    origin: str,
    segments_min_length: int,
    segments_max_length: int,
) -> list[str]:
    r1 = await return_trip_search_final_response(
        client,
        departure_after,
        destination,
        origin,
    )

    r2 = await client.trips().get_trips_by_trip_search_id(r1["data"]["id"])
    logging.info("get_trips_by_trip_search_id: %s", json.dumps(r2, indent=4))

    reduced_trip_ids = []
    for trip_item in r2["data"]:
        segments_amount = len(trip_item["relationships"]["segments"]["data"])
        if segments_min_length <= segments_amount <= segments_max_length:
            reduced_trip_ids.append(trip_item["id"])
    logging.info("reduced_trip_ids: %s", reduced_trip_ids)

    return reduced_trip_ids


async def return_trip_search_final_response(
    client: Client,
    departure_after: str,
    destination: str,
    origin: str,
) -> dict[str, Any]:
    do_condition = True
    safety_counter = 0
    response = await client.trips().create_trip_search(
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
            r1 = await client.trips().get_trip_search_by_id(response["data"]["id"])
            status = r1["data"]["attributes"]["status"]
            safety_counter += 1
    return response
