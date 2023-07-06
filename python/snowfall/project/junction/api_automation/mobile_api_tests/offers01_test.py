import asyncio
import datetime
import json
import logging
from collections.abc import Sequence

import pytest

from snowfall.project.junction.api_automation.backend_api_tests.offers01_test import (
    get_trip_ids,
    return_trip_offer_search_id,
)
from snowfall.project.junction.api_automation.test_functions.mobile_client import (
    MobileApiClient,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.skip(reason="temporary skipped")
async def test_trip_offer_search_id(
    mobile_client: MobileApiClient,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> None:
    r3 = await mobile_client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))

    assert r3["data"]["id"]


@pytest.mark.skip(reason="temporary skipped")
async def test_trip_offer_search_offers(
    mobile_client: MobileApiClient,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> None:
    r3 = await mobile_client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))

    assert r3["data"]["id"]


async def return_trip_offer_search_ids(
    mobile_client: MobileApiClient,
    departure_after: str,
    destination: str,
    origin: str,
) -> Sequence[str]:
    trip_ids = await get_trip_ids(
        mobile_client,
        departure_after,
        destination,
        origin,
    )
    await asyncio.sleep(10)

    trip_offer_search_ids = []
    for trip_id in trip_ids:
        trip_offer_search_id = await return_trip_offer_search_id(
            mobile_client,
            [trip_id],
            1992,
            4,
            29,
        )
        trip_offer_search_ids.append(trip_offer_search_id)

    return trip_offer_search_ids
