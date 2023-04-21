import asyncio
import base64
import datetime
import pathlib
from typing import AsyncIterator, Mapping, Sequence
from unittest import mock

import currencycloud
import httpx
import mongomock_motor
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fakeredis import aioredis as fakeredis
from motor import motor_asyncio
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import currencies
from snowfall.project.pay.service.accounts import accounts
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.repositories import (
    BeneficiaryRepository,
    CompanyRepository,
    ConversionRepository,
    CurrencyRepository,
    TransactionRepository,
)
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.quotations import quotations
from snowfall.project.pay.service.quotations.v1alpha.models_pb2 import (
    QuotationAmounts,
    QuotationRates,
)
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import Transaction
from snowfall.service.authentication.auth import JWTFactory
from snowfall.service.authentication.v1alpha.models_pb2 import User
from snowfall.stdlib import money, string
from snowfall.stdlib.format.jwt import Encoder
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.persistence import cursor, filesystem
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse
from snowfall.vendor.currency_cloud.models.beneficiary import BeneficiaryResponse


@pytest.fixture()
def transaction_ids() -> Sequence[str]:
    return [
        "e719b289-982c-42f0-99a2-63fa70f8f8c0",
        "c36649e6-71f1-4dfa-aa5a-01c0ede6e538",
    ]


@pytest.fixture()
def rsa_private_key() -> rsa.RSAPrivateKey:
    public_exponent = 65537
    key_size = 2048
    return rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
    )


@pytest.fixture()
def private_key(rsa_private_key: rsa.RSAPrivateKey) -> str:
    encrypted_pem_private_key = rsa_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return encrypted_pem_private_key.decode()


@pytest.fixture()
def public_key(rsa_private_key: rsa.RSAPrivateKey) -> str:
    pem_public_key = rsa_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_public_key.decode()


@pytest.fixture()
def custom_middlewares(public_key: str) -> Sequence[Middleware]:
    return [
        Middleware(
            authentication.AuthenticationMiddleware,
            backend=authenticator.Authenticator(
                public_key_content=base64.b64encode(public_key.encode()).decode(),
            ),
            on_error=handlers.auth_error_handler,
        ),
    ]


def _create_app(  # noqa: WPS211
    cc_client: currencycloud.Client,
    payment_client: PaymentClient,
    currencies_client: currencies.Client,
    quotations_repository: quotations.QuotationsRepository,
    redis_repository: UserSessionRepository,
    transactions_repository: TransactionRepository,
    conversion_repository: ConversionRepository,
    companies_repository: CompanyRepository,
    currencies_repository: CurrencyRepository,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_routes(
            bootstrap.create_dependencies(
                cc_client,
                currencies_client,
                quotations_repository,
                redis_repository,
                transactions_repository,
                conversion_repository,
                companies_repository,
                currencies_repository,
                payment_client=payment_client,
            ),
        ),
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


def _create_admin_app(  # noqa: WPS211
    cc_client: currencycloud.Client,
    payment_client: PaymentClient,
    authentication_client: auth.Client,
    companies_repository: CompanyRepository,
    contacts_repository: accounts.ContactsRepository,
    accounts_repository: accounts.AccountsRepository,
    conversions_repository: ConversionRepository,
    transactions_repository: TransactionRepository,
    currencies_repository: CurrencyRepository,
    beneficiaries_repository: BeneficiaryRepository,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_admin_routes(
            bootstrap.create_admin_dependencies(
                cc_client,
                authentication_client,
                companies_repository,
                contacts_repository,
                accounts_repository=accounts_repository,
                conversions_repository=conversions_repository,
                transactions_repository=transactions_repository,
                currencies_repository=currencies_repository,
                beneficiaries_repository=beneficiaries_repository,
                payment_client=payment_client,
            ),
        ),
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


@pytest.fixture()
def redis_client(redis_client: fakeredis.FakeRedis) -> redis.Client[str]:
    return redis.Client(
        redis_client,
        prefix="pay_api",
    )


@pytest.fixture()
async def redis_repository(
    redis_client: redis.Client[str],
) -> UserSessionRepository:
    return UserSessionRepository(
        redis_client,
        datetime.timedelta(minutes=15),  # noqa: WPS432
    )


@pytest.fixture()
def cc_login() -> str:
    return "cc_login"


@pytest.fixture()
def cc_api_key() -> str:
    return "random_key"


@pytest.fixture()
def cc_env() -> str:
    return "demo"


@pytest.fixture()
def mongo_client() -> motor_asyncio.AsyncIOMotorClient:
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture()
def quotations_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> quotations.QuotationsRepository:
    return quotations.QuotationsRepository(
        collection=mongo_client.test.quotations,
    )


@pytest.fixture()
def contacts_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> accounts.ContactsRepository:
    return accounts.ContactsRepository(
        collection=mongo_client.test.contacts,
    )


@pytest.fixture()
def accounts_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> accounts.AccountsRepository:
    return accounts.AccountsRepository(
        collection=mongo_client.test.accounts,
    )


@pytest.fixture()
async def companies_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> CompanyRepository:
    return CompanyRepository(
        collection=mongo_client.test.companies,
    )


def get_transaction(transaction_id: str) -> Transaction:
    money_usd = money.from_string("1000", money.Currency("USD")).protobuf()

    return Transaction(
        id=transaction_id,
        external_reference_id=string.uuid(),
        invoice_reference_id=string.uuid(),
        conversion_id=string.uuid(),
        amounts=QuotationAmounts(
            beneficiary=money_usd,
            base_converted=money_usd,
            fx_margin=money_usd,
            fx_provider_margin=money_usd,
            sales_margin=money_usd,
            quotation=money_usd,
        ),
        rates=QuotationRates(
            fx_quote=float(1),
            fx_buffer=float(1),
            fx_markup=float(1),
            sales_markup=float(1),
        ),
        payer_id=string.uuid(),
        beneficiary_id=string.uuid(),
    )


@pytest.fixture()
async def transactions_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
    transaction_ids: Sequence[str],
) -> TransactionRepository:
    repository = TransactionRepository(
        collection=mongo_client.test.transactions,
    )
    await asyncio.gather(
        *[
            repository.insert(get_transaction(transaction_id))
            for transaction_id in transaction_ids
        ],
    )

    return repository


@pytest.fixture()
def conversions_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> ConversionRepository:
    return ConversionRepository(
        collection=mongo_client.test.conversions,
    )


@pytest.fixture()
def currencies_repository(
    available_currencies: Sequence[money.Currency],
) -> CurrencyRepository:
    return CurrencyRepository(available_currencies)


@pytest.fixture()
def beneficiaries_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> BeneficiaryRepository:
    return BeneficiaryRepository(collection=mongo_client.test.beneficiaries)


@pytest.fixture()
def available_currencies() -> Sequence[money.Currency]:
    return [
        money.Currency("USD"),
        money.Currency("GBP"),
        money.Currency("AMD"),
        money.Currency("SEK"),
    ]


@pytest.fixture()
def cc_client(cc_login: str, cc_api_key: str, cc_env: str) -> currencycloud.Client:
    return currencycloud.Client(
        cc_login,
        cc_api_key,
        cc_env,
    )


@pytest.fixture()
def beneficiary_response() -> BeneficiaryResponse:
    return BeneficiaryResponse(
        bank_country="GB",
        currency="SEK",
        beneficiary_company_name="Company",
        beneficiary_address=["Street name 7"],
        beneficiary_country="GB",
        account_number=None,
        bic_swift="AAAABBCC123",
        iban="GB06BARC12314512778232",
        bank_address=["Street name 7"],
        bank_name="BankName",
        bank_account_type="savings",
        beneficiary_city="London",
        beneficiary_postcode="12345",
        beneficiary_state_or_province="California",
        payment_types=["priority", "regular"],
        beneficiary_entity_type="company",
        name="Company",
        bank_account_holder_name="bankAccountHolderName",
        email="example@email.com",
        aba=None,
        identifier="e82060fe-894f-43e0-9b96-3ffaf6117431",
    )


@pytest.fixture()
def payment_client(
    accounts_list_from_cc: Sequence[mock.Mock],
    balance: BalanceResponse,
    beneficiary_response: BeneficiaryResponse,
) -> mock.Mock:
    payment_client = mock.Mock()
    message = "Conversion of GBP equivalent 0.89 is less than your lower limit of 1.00"
    payment_client.create_conversion = mock.Mock(
        side_effect=CurrencyCloudError(messages=[message]),
    )

    def _get_all_accounts(  # noqa: WPS430
        page_index: int,
    ) -> Sequence[mock.Mock]:
        if page_index == 1:
            return accounts_list_from_cc

        return []

    payment_client.get_all_accounts = _get_all_accounts

    payment_client.add_currency_into_account = mock.Mock(return_value=balance)

    payment_client.validate_beneficiary = mock.Mock()

    payment_client.create_beneficiary = mock.Mock(return_value=beneficiary_response)

    return payment_client


@pytest.fixture()
def currencies_client() -> mock.Mock:
    return mock.Mock()


@pytest.fixture()
def authentication_client() -> auth.DictClient:
    return auth.DictClient()


@pytest.fixture()
def jwt_token(private_key: str) -> str:
    jwt_encoder = Encoder(
        private_key=base64.b64encode(private_key.encode()).decode(),
        algorithm="RS256",
    )
    jwt_factory = JWTFactory(
        ttl=datetime.timedelta(hours=1),
    )
    user = User(email="example@example.com", id=string.uuid())

    return jwt_encoder.encode(
        jwt_factory.from_user(user),
    )


# TODO: need to use our authentication mechanism to generate jwt token and include it
# TODO: into the headers, also create fixture for middlewares and use it
@pytest.fixture()
def headers(jwt_token: str) -> dict[str, str]:
    return {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    cc_client: currencycloud.Client,
    currencies_client: currencies.Client,
    quotations_repository: quotations.QuotationsRepository,
    redis_repository: UserSessionRepository,
    transactions_repository: TransactionRepository,
    conversions_repository: ConversionRepository,
    payment_client: PaymentClient,
    companies_repository: CompanyRepository,
    currencies_repository: CurrencyRepository,
) -> applications.Starlette:
    return _create_app(
        cc_client=cc_client,
        payment_client=payment_client,
        currencies_client=currencies_client,
        quotations_repository=quotations_repository,
        redis_repository=redis_repository,
        transactions_repository=transactions_repository,
        conversion_repository=conversions_repository,
        companies_repository=companies_repository,
        currencies_repository=currencies_repository,
        openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
    )


@pytest.fixture()
def admin_app(  # noqa: WPS211
    cc_client: currencycloud.Client,
    authentication_client: auth.Client,
    companies_repository: CompanyRepository,
    payment_client: PaymentClient,
    contacts_repository: accounts.ContactsRepository,
    accounts_repository: accounts.AccountsRepository,
    conversions_repository: ConversionRepository,
    transactions_repository: TransactionRepository,
    currencies_repository: CurrencyRepository,
    beneficiaries_repository: BeneficiaryRepository,
    custom_middlewares: Sequence[Middleware],
) -> applications.Starlette:
    return _create_admin_app(
        cc_client=cc_client,
        payment_client=payment_client,
        authentication_client=authentication_client,
        companies_repository=companies_repository,
        contacts_repository=contacts_repository,
        accounts_repository=accounts_repository,
        conversions_repository=conversions_repository,
        transactions_repository=transactions_repository,
        currencies_repository=currencies_repository,
        beneficiaries_repository=beneficiaries_repository,
        custom_middlewares=custom_middlewares,
        openapi_path=filesystem.resource_path("junction.pay_admin_api", "openapi.json"),
    )


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
async def admin_client(
    admin_app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=admin_app,
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client
