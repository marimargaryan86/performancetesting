import dataclasses
import json
import pkgutil
import zoneinfo
from typing import Mapping, Optional, Sequence

from snowfall.stdlib import h3


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
