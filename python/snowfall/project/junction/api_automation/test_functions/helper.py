import asyncio
import time
from collections.abc import Sequence
from io import BytesIO
from typing import Any

import pandas as pd
from pymongo import MongoClient

from snowfall.project.junction.api_automation.conftest import connect_to_aws


async def wait_until_completed(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 5,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while stopwatch - time.time() > 0:
        response = await request_func()
        if response["attributes"]["status"] == "completed":
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)


async def wait_for_response(
    request_func: Any,
    error_message: str,
    max_wait_time_seconds: int = 120,
    polling_interval: int = 10,
) -> Any:
    stopwatch = time.time() + max_wait_time_seconds

    while stopwatch - time.time() > 0:
        response = await request_func()
        if response["data"]:
            return response
        await asyncio.sleep(polling_interval)

    raise AssertionError(error_message)


def get_places() -> list[tuple[str, str]]:
    data = connect_to_aws()
    o_d_combination = pd.read_csv(BytesIO(data), sep=";")
    origin_values = o_d_combination["Origin"].tolist()
    destination_values = o_d_combination["Destination"].tolist()
    return list(zip(origin_values, destination_values, strict=False))


async def get_coordinates_by_place_name(
    mongo_client: MongoClient[Any],
    place_pairs: Sequence[tuple[Any, Any]],
) -> list[tuple[Any, Any]]:
    place_id_pairs = []
    for place in place_pairs:
        place_result = mongo_client["places"]["places"].find_one(
            filter={"location.name": place},
        )
        coordinate0, coordinate1 = None, None
        if place_result is not None:
            coordinates = place_result.get("location")
            if coordinates is not None:
                coordinate0, coordinate1 = coordinates.get("coordinates").get(
                    "coordinates",
                )
        place_id_pairs.append((coordinate1, coordinate0))

    return place_id_pairs
