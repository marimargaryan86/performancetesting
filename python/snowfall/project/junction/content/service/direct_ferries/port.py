import dataclasses
import json
import pkgutil
import zoneinfo
from collections.abc import Mapping

import timezonefinder

from snowfall.stdlib import h3

_tz_finder = timezonefinder.TimezoneFinder()


@dataclasses.dataclass(frozen=True)
class Port(h3.CoordinatesItem):
    name: str | None


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
        "snowfall.project.junction.content.service.direct_ferries.port",
        "ports.json",
    )

    if json_content is None:
        raise RuntimeError("port.json not found")

    ports = json.loads(json_content.decode("utf-8"))

    return [_make_port(port) for port in ports]
