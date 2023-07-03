import datetime
from collections.abc import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.adapter import authentication
from snowfall.project.pay.adapter import (
    accounts,
    companies,
    contacts,
    conversions,
    currencies,
    payments,
    quotations,
    transactions,
)
from snowfall.project.pay.service.pay_api import includes
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    ConversionRepository,
    TransactionRepository,
)
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.currency_cloud import client


class Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_address: str
    currencies_address: str
    authentication_address: str
    transactions_address: str
    jwt_public_key: str
    ory_jwk_ttl: datetime.timedelta = datetime.timedelta(hours=1)
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]


class AdminSettings(Settings):
    companies_address: str
    payments_address: str


def create_admin_dependencies(  # noqa: WPS211
    authentication_client: authentication.Client,
    conversions_repository: ConversionRepository,
    beneficiaries_repository: BeneficiaryRepository,
    transactions_repository: TransactionRepository,
    accounts_client: accounts.GrpcClient,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    cc_payment_client: client.PaymentClient,
    transactions_client: transactions.Client,
    conversions_client: conversions.Client,
    currencies_client: currencies.Client,
    payments_client: payments.GrpcClient,
) -> lagom.Container:
    container = lagom.Container()
    container[client.PaymentClient] = cc_payment_client
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[TransactionRepository] = transactions_repository
    container[ConversionRepository] = conversions_repository
    container[BeneficiaryRepository] = beneficiaries_repository
    container[accounts.GrpcClient] = accounts_client
    container[companies.Client] = companies_client  # type: ignore[type-abstract]
    container[contacts.Client] = contacts_client  # type: ignore[type-abstract]
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    container[conversions.Client] = conversions_client  # type: ignore[type-abstract]
    container[payments.GrpcClient] = payments_client
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]

    includes.register_resolvers(transactions_client)

    return container


def create_dependencies(  # noqa: WPS211
    currencies_client: currencies.Client,
    redis_client: UserSessionRepository,
    transactions_repository: TransactionRepository,
    transactions_client: transactions.Client,
    quotations_client: quotations.Client,
    conversions_repository: ConversionRepository,
    payment_client: client.PaymentClient,
) -> lagom.Container:
    container = lagom.Container()
    container[client.PaymentClient] = payment_client
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[quotations.Client] = quotations_client  # type: ignore[type-abstract]
    container[UserSessionRepository] = redis_client
    container[TransactionRepository] = transactions_repository
    container[ConversionRepository] = conversions_repository
    container[transactions.Client] = transactions_client  # type: ignore[type-abstract]
    return container
