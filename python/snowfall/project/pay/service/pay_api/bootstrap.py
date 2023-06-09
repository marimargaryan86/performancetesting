from typing import Sequence

import lagom
from pydantic import AnyUrl

from snowfall.adapter import authentication
from snowfall.project.pay.adapter import accounts, currencies, payments
from snowfall.project.pay.service.accounts.repositories import ContactsRepository
from snowfall.project.pay.service.pay_api import includes
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    ConversionRepository,
    CurrencyRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.quotations import quotations
from snowfall.stdlib import money
from snowfall.stdlib.integration.starlette import application
from snowfall.vendor.currency_cloud import client


class Settings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_env: str
    cc_address: str
    currencies_address: str
    authentication_address: str
    jwt_public_key: str
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    currencies: Sequence[money.Currency]


class AdminSettings(application.Settings):
    cc_login: str
    cc_api_key: str
    cc_env: str
    cc_address: str
    authentication_address: str
    accounts_address: str
    payments_address: str
    jwt_public_key: str
    mongo_dsn: Sequence[AnyUrl]
    redis_dsn: Sequence[AnyUrl]
    currencies: Sequence[money.Currency]


def create_admin_dependencies(  # noqa: WPS211
    authentication_client: authentication.Client,
    companies_repository: CompanyRepository,
    contacts_repository: ContactsRepository,
    conversions_repository: ConversionRepository,
    transactions_repository: TransactionRepository,
    currencies_repository: CurrencyRepository,
    beneficiaries_repository: BeneficiaryRepository,
    accounts_client: accounts.GrpcClient,
    cc_payment_client: client.PaymentClient,
    payments_client: payments.GrpcClient,
) -> lagom.Container:
    container = lagom.Container()
    container[client.PaymentClient] = cc_payment_client
    container[authentication.Client] = authentication_client  # type: ignore[type-abstract]
    container[CompanyRepository] = companies_repository
    container[ContactsRepository] = contacts_repository
    container[ConversionRepository] = conversions_repository
    container[TransactionRepository] = transactions_repository
    container[CurrencyRepository] = currencies_repository
    container[BeneficiaryRepository] = beneficiaries_repository
    container[accounts.GrpcClient] = accounts_client
    container[payments.GrpcClient] = payments_client

    includes.register_resolvers(transactions_repository)

    return container


def create_dependencies(  # noqa: WPS211
    currencies_client: currencies.Client,
    quotations_repository: quotations.QuotationsRepository,
    redis_client: UserSessionRepository,
    transactions_repository: TransactionRepository,
    conversions_repository: ConversionRepository,
    companies_repository: CompanyRepository,
    currencies_repository: CurrencyRepository,
    payment_client: client.PaymentClient,
) -> lagom.Container:
    container = lagom.Container()
    container[client.PaymentClient] = payment_client
    container[currencies.Client] = currencies_client  # type: ignore[type-abstract]
    container[quotations.QuotationsRepository] = quotations_repository
    container[UserSessionRepository] = redis_client
    container[TransactionRepository] = transactions_repository
    container[ConversionRepository] = conversions_repository
    container[CompanyRepository] = companies_repository
    container[CurrencyRepository] = currencies_repository
    return container
