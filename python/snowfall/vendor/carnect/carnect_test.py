import os

import pytest

from snowfall.vendor.carnect import client
from snowfall.vendor.carnect.builders.ping_builder import PingRqBuilder

disable_by_default = pytest.mark.skipif(
    os.getenv("CARNECT_TESTS") != "ENABLED",
    reason="To enable set env variable CARNECT_TESTS=ENABLED",
)


@disable_by_default
async def test_ping(carnect_client: client.CarnectClient) -> None:
    rq = PingRqBuilder()
    rq.add_echo("test")
    rs = await carnect_client.ping(rq.build())
    assert rs.ping_rs is not None
    assert rs.ping_rs.echo_data == ["test"]
