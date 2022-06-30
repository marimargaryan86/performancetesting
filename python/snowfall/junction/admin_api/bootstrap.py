import ipaddress
from typing import Sequence

import lagom
from lagom.integrations import starlette

from snowfall.adapter import places
from snowfall.stdlib import service


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80
    places_address: Sequence[str]


def create_dependencies(
    places_client: places.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[places.Client] = places_client  # type: ignore[misc]

    return starlette.StarletteIntegration(container)
