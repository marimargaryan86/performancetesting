import ipaddress
from typing import Sequence

import currencycloud
import lagom
from lagom.integrations import starlette

from snowfall.stdlib import service


class Settings(service.Settings):
    forwarded_allowed_ips: Sequence[ipaddress.IPv4Address] = [
        ipaddress.IPv4Address("127.0.0.1"),
    ]
    http_address: ipaddress.IPv4Address = ipaddress.IPv4Address("127.0.0.1")
    http_port: int = 8000
    cc_login: str
    cc_api_key: str
    cc_env: str


def create_dependencies(
    cc_client: currencycloud.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[currencycloud.Client] = cc_client
    return starlette.StarletteIntegration(container)
