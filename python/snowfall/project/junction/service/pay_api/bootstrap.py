from typing import Sequence

import currencycloud
import lagom

from snowfall.project.adapter import authentication
from snowfall.project.junction.adapter import currencies
from snowfall.project.junction.service.pay_api.repositories import CompanyRepository
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_env: str
    currencies_address: Sequence[str]
    mongo_dsn: str
    authentication_address: str
    jwt_public_key: str


def create_dependencies(
    cc_client: currencycloud.Client,
    currencies_client: currencies.Client,
    authentication_client: authentication.Client,
    companies_repository: CompanyRepository,
) -> lagom.Container:
    container = lagom.Container()
    container[currencycloud.Client] = cc_client
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[CompanyRepository] = companies_repository
    return container
