import dataclasses
import json
import pkgutil
import zoneinfo
from typing import Mapping, Optional, Sequence

import aiofiles
import timezonefinder

from snowfall.stdlib import h3
from snowfall.vendor.direct_ferries.models import route

_tz_finder = timezonefinder.TimezoneFinder()


@dataclasses.dataclass(frozen=True)
class Port(h3.CoordinatesItem):
    name: Optional[str]


def _make_port(port: Mapping[str, str | float]) -> Port:
    return Port(
        identifier=str(port["id"]),
        name=str(port["name"]),
        latitude=float(port["latitude"]),
        longitude=float(port["longitude"]),
        timezone=zoneinfo.ZoneInfo(str(port["timezone"])),
    )


def load_ports() -> list[Port]:
    json_content = pkgutil.get_data(
        "snowfall.project.junction.service.providers.direct_ferries.main",
        "ports.json",
    )

    if json_content is None:
        return []  # TODO: throw exception

    ports = json.loads(json_content.decode("utf-8"))

    return [_make_port(port) for port in ports]


class PortRepository(object):
    def __init__(self, ports: Sequence[Port]) -> None:
        self._ports = {port.identifier: port for port in ports}

    def get_by_id(self, identifier: str) -> Port:
        return self._ports[identifier]


async def make_ports_from_routes(  # noqa: WPS231
    routes: Sequence[route.Route],
    output_path: str | None = None,
) -> None:
    seen_ports = set()
    ports = []

    async with aiofiles.open(output_path or "ports.json", "a+") as out_file:
        for route_obj in routes:
            for port in (route_obj.port_from, route_obj.port_to):
                if port.code not in seen_ports:
                    ports.append(
                        {
                            "id": port.code,
                            "name": port.name or port.code,
                            "latitude": float(port.latitude),
                            "longitude": float(port.longitude),
                            "timezone": str(
                                zoneinfo.ZoneInfo(
                                    _tz_finder.timezone_at(
                                        lat=port.latitude,
                                        lng=port.longitude,
                                    )
                                    or "",
                                ),
                            ),
                        },
                    )
                    seen_ports.add(port.code)

        await out_file.write(json.dumps(ports, indent=4))
