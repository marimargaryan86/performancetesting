import dataclasses
import json
import pathlib
import pkgutil
import zoneinfo
from collections.abc import Mapping, Sequence

import aiofiles
import httpx
import pydantic

from snowfall.project.junction.service.providers.distribusion.config import (
    DistribusionConfig,
)
from snowfall.stdlib import h3
from snowfall.stdlib.instrumentation.httpx import logging, metrics
from snowfall.stdlib.service import application
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models.stations import Station as VendorStation


class DumpStationsSettings(DistribusionConfig, application.Settings):
    output_file: str = pydantic.Field(
        json_schema_extra={"hidden": True, "argument": True},
    )


@dataclasses.dataclass(frozen=True)
class Station(h3.CoordinatesItem):
    name: str | None


class StationRepository(object):
    def __init__(
        self,
        stations: Sequence[Station],
    ):
        self._stations = {station.identifier: station for station in stations}

    def get_by_id(self, station_id: str) -> Station:
        return self._stations[station_id]


async def dump_stations(
    app: application.Application[DumpStationsSettings],
) -> None:
    http_client = await app.stack.enter_async_context(
        httpx.AsyncClient(
            timeout=app.settings.api_timeout,
        ),
    )
    logging.register(http_client)
    metrics.register(http_client)
    distribusion_client = client.DistribusionClient(
        api_base_url=str(app.settings.api_base_url),
        api_key=app.settings.api_key,
        retailer_partner_number=app.settings.retailer_partner_number,
        http_client=http_client,
    )

    await _dump_stations(
        await distribusion_client.get_stations(),
        pathlib.Path(app.settings.output_file),
    )


async def _dump_stations(
    response: Sequence[VendorStation],
    output_file: pathlib.Path,
) -> None:
    stations = [
        {
            "id": station.code,
            "name": station.name,
            "time_zone": station.time_zone,
            "latitude": station.latitude,
            "longitude": station.longitude,
        }
        for station in response
    ]

    async with aiofiles.open(str(output_file), "w") as out_file:
        await out_file.write(json.dumps(stations, indent=4))


async def load_stations() -> list[Station]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.distribusion.stations",
        "stations.json",
    )

    if json_content is None:
        return []  # TODO: throw exception

    stations = json.loads(json_content.decode("utf-8"))
    return [await _make_station(station) for station in stations]


async def _make_station(
    station: Mapping[str, str | float],
) -> Station:
    return Station(
        identifier=str(station["id"]),
        name=str(station["name"]),
        timezone=zoneinfo.ZoneInfo(str(station["time_zone"])),
        latitude=float(station["latitude"]),
        longitude=float(station["longitude"]),
    )
