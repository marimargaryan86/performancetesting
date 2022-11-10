from typing import Sequence

import currencycloud
import lagom
from lagom.integrations import starlette

from snowfall.project.junction.adapter import currencies
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_env: str
    currencies_address: Sequence[str]


def create_dependencies(
    cc_client: currencycloud.Client,
    currencies_client: currencies.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[currencycloud.Client] = cc_client
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    return starlette.StarletteIntegration(container)
