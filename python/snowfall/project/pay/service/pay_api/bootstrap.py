from collections.abc import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.adapter import authentication
from snowfall.project.pay.adapter import (
    accounts,
    companies,
    conversions,
    currencies,
    payments,
    quotations,
    transactions,
)
from snowfall.project.pay.service.companies.repositories import ContactsRepository
from snowfall.project.pay.service.pay_api import includes
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
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
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]


class AdminSettings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_address: str
    authentication_address: str
    companies_address: str
    payments_address: str
    transactions_address: str
    jwt_public_key: str
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    currencies_address: str


def create_admin_dependencies(  # noqa: WPS211
    authentication_client: authentication.Client,
    companies_repository: CompanyRepository,
    contacts_repository: ContactsRepository,
    conversions_repository: ConversionRepository,
    beneficiaries_repository: BeneficiaryRepository,
    transactions_repository: TransactionRepository,
    accounts_client: accounts.GrpcClient,
    companies_client: companies.GrpcClient,
    cc_payment_client: client.PaymentClient,
    transactions_client: transactions.Client,
    conversions_client: conversions.Client,
    currencies_client: currencies.Client,
    payments_client: payments.GrpcClient,
) -> lagom.Container:
    container = lagom.Container()
    container[client.PaymentClient] = cc_payment_client
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[CompanyRepository] = companies_repository
    container[TransactionRepository] = transactions_repository
    container[ContactsRepository] = contacts_repository
    container[ConversionRepository] = conversions_repository
    container[BeneficiaryRepository] = beneficiaries_repository
    container[accounts.GrpcClient] = accounts_client
    container[companies.GrpcClient] = companies_client
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
    companies_repository: CompanyRepository,
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
    container[CompanyRepository] = companies_repository
    return container
