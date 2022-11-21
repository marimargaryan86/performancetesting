import datetime
import json
import logging
from typing import Sequence

import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_trip_offer_search_id(
    client: JunctionClient,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> None:
    r3 = await client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))

    assert r3["data"]["id"]


@pytest.mark.integration
async def test_trip_offer_search_offers(
    client: JunctionClient,
    trip_ids: Sequence[str],
    year: int,
    month: int,
    day: int,
) -> None:
    r3 = await client.create_offer_search(
        trip_ids=trip_ids,
        passengers_dates_of_birth=[datetime.date(year=year, month=month, day=day)],
    )
    logging.info("create_offer_search: %s", json.dumps(r3, indent=4))

    assert r3["data"]["id"]
