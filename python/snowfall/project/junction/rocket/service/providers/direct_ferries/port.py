import dataclasses
import json
import pkgutil
import zoneinfo
from collections.abc import Mapping, Sequence

import aiofiles
import timezonefinder
from geopy.distance import geodesic

from snowfall.stdlib import h3
from snowfall.stdlib.v1.latlng_pb2 import LatLng
from snowfall.vendor.direct_ferries.models import route

_tz_finder = timezonefinder.TimezoneFinder()


@dataclasses.dataclass(frozen=True)
class Port(h3.CoordinatesItem):
    name: str


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
        package="snowfall.project.junction.rocket.service.providers.direct_ferries.port",
        resource="ports.json",
    )

    if json_content is None:
        raise RuntimeError("Ports not found")

    ports = json.loads(json_content.decode("utf-8"))

    return [_make_port(port) for port in ports]


def get_closest_port(coordinates: LatLng, ports: Sequence[Port]) -> Port:
    closest_port: Port = ports[0]
    closest_distance = float("inf")

    for port in ports:
        distance = geodesic(
            (coordinates.latitude, coordinates.longitude),
            (port.latitude, port.longitude),
        ).kilometers

        if distance < closest_distance:
            closest_distance = distance
            closest_port = port

    return closest_port


class PortRepository:
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
