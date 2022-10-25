import logging

import pytest

from snowfall.project.junction.api_automation.legs_test import (
    return_get_segment_by_id_response,
)
from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_get_leg_by_id(
    client: JunctionClient,
    departure_after: str,
    origin: str,
    destination: str,
) -> None:
    r3 = await return_get_segment_by_id_response(
        client,
        departure_after,
        destination,
        origin,
    )
    legs = r3["data"]["relationships"]["legs"]["data"]

    for leg in legs:
        leg_data = await client.legs().get_leg_by_id(leg["id"])
        assert "operator" in leg_data["data"]["attributes"]
