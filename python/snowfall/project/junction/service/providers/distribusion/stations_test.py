import os

import pytest

from snowfall.project.junction.service.providers.distribusion import stations

disable_by_default = pytest.mark.skipif(
    os.getenv("DISTRIBUSION_TESTS") != "ENABLED",
    reason="To enable set env variable DISTRIBUSION_TESTS=ENABLED",
)


@disable_by_default
@pytest.mark.asyncio
async def test_load_stations() -> None:
    station_list = await stations.load_stations()
    assert station_list
