import ipaddress
from typing import Sequence

import lagom
from lagom.integrations import starlette

from snowfall.stdlib import service


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 80


def create_dependencies() -> starlette.StarletteIntegration:
    container = lagom.Container()

    return starlette.StarletteIntegration(container)
