import contextlib
import dataclasses
import json
import pathlib
import pkgutil
import zoneinfo
from typing import Mapping, Optional, Sequence

import aiofiles
import httpx
import pydantic

from snowfall.project.junction.service.providers.distribusion.config import (
    DistribusionConfig,
)
from snowfall.stdlib import h3, service
from snowfall.vendor.distribusion import client
from snowfall.vendor.distribusion.models.stations import Station as VendorStation


class DumpStationsSettings(DistribusionConfig, service.Settings):
    output_file: str = pydantic.Field(hidden=True, argument=True)


@dataclasses.dataclass(frozen=True)
class Station(h3.CoordinatesItem):
    name: Optional[str]


async def dump_stations(app: service.Application[DumpStationsSettings]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        http_client = await stack.enter_async_context(
            httpx.AsyncClient(
                http2=True,
                timeout=app.settings.api_timeout,
            ),
        )
        distribusion_client = client.DistribusionClient(
            api_base_url=app.settings.api_base_url,
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
    stations = []

    for station in response:
        stations.append(
            {
                "id": station.code,
                "name": station.name,
                "time_zone": station.time_zone,
                "latitude": station.latitude,
                "longitude": station.longitude,
            },
        )

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
