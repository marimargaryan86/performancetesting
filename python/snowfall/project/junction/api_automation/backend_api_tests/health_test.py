import logging

import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_health(
    junction_client: JunctionClient,
) -> None:
    health_response = await junction_client.health()
    assert health_response["meta"]["status"] == "pass", "health check is not o.k."
