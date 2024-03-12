import datetime
from collections.abc import Sequence

import lagom
from pydantic import AnyUrl, RedisDsn

from snowfall.adapter import authentication
from snowfall.project.pay.adapter import (
    companies,
    currencies,
    quotations,
    transactions,
)
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.stdlib.integration.starlette import application


class _Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_address: str
    authentication_address: str
    transactions_address: str
    companies_address: str
    jwt_public_key: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: RedisDsn


class Settings(_Settings):
    currencies_address: str


class AdminSettings(_Settings):
    payments_address: str


def create_admin_dependencies(
    authentication_client: authentication.Client,
    transactions_client: transactions.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    return container


def create_dependencies(
    redis_client: UserSessionRepository,
    quotations_client: quotations.Client,
    currencies_client: currencies.Client,
    companies_client: companies.Client,
    transactions_client: transactions.Client,
) -> lagom.Container:
    container = lagom.Container()
    container[quotations.Client] = quotations_client  # type: ignore[type-abstract]
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    container[UserSessionRepository] = redis_client
    return container
