import os

import pytest

from snowfall.vendor.carnect import client
from snowfall.vendor.carnect.builders.location_search_builder import (
    LocationSearchRqBuilder,
)
from snowfall.vendor.carnect.builders.ping_builder import PingRqBuilder
from snowfall.vendor.carnect.models.service import VehLocationSearchRqTarget

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


@disable_by_default
async def test_search_location(carnect_client: client.CarnectClient) -> None:
    rq = LocationSearchRqBuilder()
    criterion = rq.add_search_criterion()
    criterion.add_geo_point(51.5072, 0.1276)
    criterion.radius_km(50)
    criterion.ranking(100)
    rq.target(target=VehLocationSearchRqTarget.TEST)

    pos_source = rq.pos().add_source()
    pos_source.iso_country("EN")
    pos_source.user_name("CarnectNet")
    pos_source.password("1lK3F98B")
    rq.pos().add_source().iso_country("GB")

    rs = await carnect_client.location_search(rq.build())
    assert rs.veh_location_search_rs is not None
