import datetime
import zoneinfo
from unittest import mock

import aiofiles
import pytest
from xsdata.formats.dataclass import parsers
from xsdata.formats.dataclass.parsers import config as parsers_config

from snowfall.project.junction.rocket.service.providers.silverrail import (
    adapter as silverrail_adapter,
)
from snowfall.project.junction.rocket.service.providers.silverrail import train_stations
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.silverrail.models import shopping


async def _load_xml_fixture(
    file_name: str,
    package: str | None = None,
) -> bytes:
    if not package:
        package = __name__

    file_path = filesystem.resource_path(
        package=package,
        resource="fixtures/{file_name}.xml".format(
            file_name=file_name.removesuffix(".xml"),
        ),
    )

    async with aiofiles.open(file_path, "rb") as file_handle:
        return await file_handle.read()


async def get_shopping_point_to_point_response() -> (
    shopping.PointToPointShoppingResponse
):
    parser = parsers.XmlParser(
        config=parsers_config.ParserConfig(fail_on_unknown_properties=False),
    )
    response = await _load_xml_fixture("point_to_point_shopping.xml")

    output: shopping.ShoppingPointToPointShopOutput = parser.from_bytes(
        response,
        shopping.ShoppingPointToPointShopOutput,
    )
    if not output.body or output.body.point_to_point_shopping_response is None:
        raise RuntimeError("Wrong configured fixture")

    return output.body.point_to_point_shopping_response


@pytest.fixture()
async def train_station_repository() -> train_stations.TrainStationRepository:
    return train_stations.TrainStationRepository([
        train_stations.TrainStation(
            name="first",
            identifier="FRLYS",
            latitude=48.8448404,
            longitude=2.3744416,
            timezone=zoneinfo.ZoneInfo("America/Winnipeg"),
        ),
        train_stations.TrainStation(
            name="second",
            identifier="FRXYD",
            latitude=45.7611339,
            longitude=4.8527867,
            timezone=zoneinfo.ZoneInfo("America/Winnipeg"),
        ),
        train_stations.TrainStation(
            name="segment station",
            identifier="FRPBE",
            latitude=48.8385918,
            longitude=2.3784756,
            timezone=zoneinfo.ZoneInfo("America/Winnipeg"),
        ),
    ])


@pytest.fixture()
async def silverrail_search_result_generator(
    train_station_repository: train_stations.TrainStationRepository,
) -> silverrail_adapter.SilverrailOffersAdapter:
    return silverrail_adapter.SilverrailOffersAdapter(
        silverrail_client=mock.Mock(
            name="SilverRailClient",
            shopping_point_to_point=mock.AsyncMock(
                name="shopping_point_to_point",
                return_value=await get_shopping_point_to_point_response(),
            ),
        ),
        train_station_repository=train_station_repository,
        ttl=datetime.timedelta(seconds=15),
    )
