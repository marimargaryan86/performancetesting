import logging

import pytest

from snowfall.vendor.junction.go.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_health(
    junction_client: Client,
) -> None:
    health_response = await junction_client.health()
    assert health_response["meta"]["status"] == "pass", "health check is not o.k."
