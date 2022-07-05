import currencycloud
import lagom
from lagom.integrations import starlette

from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_env: str


def create_dependencies(
    cc_client: currencycloud.Client,
) -> starlette.StarletteIntegration:
    container = lagom.Container()
    container[currencycloud.Client] = cc_client
    return starlette.StarletteIntegration(container)
