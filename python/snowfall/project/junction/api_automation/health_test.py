import logging

import httpx
import pytest

from snowfall.vendor.junction.client import JunctionClient

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_health(
    host: str,
    api_token: str,
) -> None:
    client = JunctionClient(
        api_url="https://{0}".format(host),
        token=api_token,
        client=httpx.AsyncClient(timeout=10),
    )

    health_response = await client.health()
    assert health_response["meta"]["status"] == "pass", "health check is not o.k."
