import datetime
import pathlib
import random
from collections.abc import AsyncIterator, Mapping, Sequence
from unittest import mock

import httpx
import pytest
from fakeredis import aioredis as fakeredis
from motor import core
from starlette import applications
from starlette.middleware import Middleware, authentication

from snowfall.adapter import authentication as auth
from snowfall.adapter.authentication import JWTFactory
from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter import (
    accounts,
    beneficiaries,
    companies,
    contacts,
    conversions,
    currencies,
    payments,
    quotations,
    refunds,
    transactions,
)
from snowfall.project.pay.service.pay_api import authenticator, bootstrap
from snowfall.project.pay.service.pay_api import repositories as pay_repos
from snowfall.project.pay.service.pay_api.cache import UserSessionRepository
from snowfall.project.pay.service.pay_api.routes import router
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import (
    Quotation,
    QuotationAmounts,
    QuotationRates,
    Transaction,
)
from snowfall.service.authentication.v1.models_pb2 import User
from snowfall.stdlib import money, string
from snowfall.stdlib.format import jwt
from snowfall.stdlib.integration.starlette import application, handlers
from snowfall.stdlib.integration.starlette import authentication as stdlib_auth
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
def quotations_ids() -> list[str]:
    return [
        "766f0893-727e-430c-9531-ebb01d579b2d",
    ]


@pytest.fixture()
async def booking_id(
    transaction_ids: Sequence[str],
    transactions_client: transactions.Client,
) -> str:
    return (await transactions_client.get(transaction_ids[0])).external_reference_id


async def mock_jwt_to_user_id(token: str) -> str:
    return authenticator.LegacyAuth(jwt.Decoder()).get_user_id_from_jwt(token)


@pytest.fixture()
def custom_middlewares() -> Sequence[Middleware]:
    return [
        Middleware(
            authentication.AuthenticationMiddleware,
            backend=stdlib_auth.JWTAuthenticationBackend(
                jwt_to_user_id=mock_jwt_to_user_id,
            ),
            on_error=handlers.auth_error_handler,
        ),
    ]


def _create_app(  # noqa: WPS211
    payment_client: PaymentClient,
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    redis_repository: UserSessionRepository,
    conversion_repository: pay_repos.ConversionRepository,
    transactions_client: transactions.Client,
    companies_client: companies.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_routes(
            bootstrap.create_dependencies(
                currencies_client,
                redis_repository,
                transactions_client,
                quotations_client,
                companies_client,
                conversion_repository,
                payment_client=payment_client,
            ),
        ),
    )
    app.add_exception_handler(cursor.CursorError, handlers.cursor_error_handler)
    app.add_exception_handler(errors.NotFoundError, handlers.not_found_error_handler)

    return app


def _create_admin_app(  # noqa: WPS211
    cc_payment_client: PaymentClient,
    authentication_client: auth.Client,
    accounts_client: accounts.GrpcClient,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    payment_client: payments.GrpcClient,
    conversions_repository: pay_repos.ConversionRepository,
    transactions_client: transactions.Client,
    conversions_client: conversions.Client,
    currencies_client: currencies.Client,
    beneficiaries_client: beneficiaries.Client,
    refunds_client: refunds.Client,
    openapi_path: pathlib.Path,
    custom_middlewares: Sequence[Middleware] | None = None,
) -> applications.Starlette:
    app = application.create_starlette_app(
        custom_middlewares=custom_middlewares,
        openapi_path=openapi_path,
        routes=router.get_admin_routes(
            bootstrap.create_admin_dependencies(
                authentication_client,
                conversions_repository=conversions_repository,
                beneficiaries_client=beneficiaries_client,
                accounts_client=accounts_client,
                companies_client=companies_client,
                contacts_client=contacts_client,
                transactions_client=transactions_client,
                conversions_client=conversions_client,
                cc_payment_client=cc_payment_client,
                currencies_client=currencies_client,
                payments_client=payment_client,
                refunds_client=refunds_client,
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
def accounts_client() -> accounts.DictClient:
    return accounts.DictClient()


@pytest.fixture()
def companies_client() -> companies.DictClient:
    return companies.DictClient(fixtures.get_companies())


@pytest.fixture()
def contacts_client() -> contacts.DictClient:
    return contacts.DictClient(
        [
            fixtures.generate_contact(fixtures.CONTACTS[0]),
            fixtures.generate_contact_with_bad_company_id(fixtures.CONTACTS[1]),
        ],
    )


@pytest.fixture()
def transactions_client(
    transaction_ids: Sequence[str],
) -> transactions.Client:
    return transactions.DictClient(
        [get_transaction(transaction_id) for transaction_id in transaction_ids],
    )


@pytest.fixture()
def conversions_client(
    transaction_ids: Sequence[str],
) -> conversions.DictClient:
    return conversions.DictClient(
        [
            fixtures.generate_conversion(conversion_id)
            for conversion_id in fixtures.CONVERSIONS
        ],
    )


@pytest.fixture()
def refunds_client(cc_payment_client: mock.Mock) -> refunds.DictClient:
    refund_data = [
        fixtures.generate_refund(refund_id) for refund_id in fixtures.REFUNDS
    ]
    return refunds.DictClient(
        refund_data,
        [get_transaction(refund.transaction_id) for refund in refund_data],
        cc_payment_client,
    )


@pytest.fixture()
def quotations_client(
    quotations_ids: Sequence[str],
) -> quotations.Client:
    return quotations.DictClient(
        [get_quotation(quotations_id) for quotations_id in quotations_ids],
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
            processing_margin=money_usd,
            sales_margin=money_usd,
            quotation=money_usd,
        ),
        rates=QuotationRates(
            fx_quote=float(1),
            fx_buffer=float(1),
            fx_markup=float(1),
            sales_markup=float(1),
            processing_markup=float(2),
        ),
        payer_id=string.uuid(),
        beneficiary_id=string.uuid(),
    )


def get_quotation(quotation_id: str) -> Quotation:
    money_usd = money.from_string("1000", money.Currency("USD")).protobuf()
    basic_rate = float(1)
    return Quotation(
        id=quotation_id,
        amounts=QuotationAmounts(
            beneficiary=money_usd,
            base_converted=money_usd,
            fx_margin=money_usd,
            processing_margin=money_usd,
            sales_margin=money_usd,
            quotation=money_usd,
        ),
        rates=QuotationRates(
            fx_quote=basic_rate,
            fx_buffer=basic_rate,
            fx_markup=basic_rate,
            sales_markup=basic_rate,
            processing_markup=basic_rate,
        ),
        payer_id=string.uuid(),
        beneficiary_id=string.uuid(),
    )


@pytest.fixture()
def conversions_repository(
    mongo_client: core.AgnosticClient,
) -> pay_repos.ConversionRepository:
    return pay_repos.ConversionRepository(
        collection=mongo_client.test.conversions,
    )


@pytest.fixture()
def beneficiaries_client() -> beneficiaries.DictClient:
    return beneficiaries.DictClient(
        (
            beneficiaries.models_pb2.Beneficiary(  # type: ignore[attr-defined]
                id=string.uuid(),
                external_reference=string.uuid(),
                account_id=string.uuid(),
                created_by="ByMe",
                updated_by="ByMe",
                payment_type="priority",
                currency="USD",
            ),
        ),
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
        identifier="e82060fe-894f-43e0-9b96-3ffaf6117431",
    )


@pytest.fixture()
def cc_payment_client(
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

    payment_client.add_currency_into_account = mock.AsyncMock(return_value=balance)

    payment_client.validate_beneficiary = mock.AsyncMock()

    payment_client.create_beneficiary = mock.AsyncMock(
        return_value=beneficiary_response,
    )

    detailed_rate = mock.Mock()
    detailed_rate.client_buy_amount = random.randint(1, 10000)  # noqa: S311, WPS432
    payment_client.get_detailed_rates = mock.AsyncMock(
        return_value=detailed_rate,
    )

    return payment_client


@pytest.fixture()
def authentication_client() -> auth.DictClient:
    return auth.DictClient()


@pytest.fixture()
def payment_client() -> payments.Client:
    return payments.DictClient(fixtures.get_payments())


@pytest.fixture()
def jwt_token() -> str:
    return jwt.Encoder().encode(
        JWTFactory(
            ttl=datetime.timedelta(hours=1),
        ).from_user(User(email="example@example.com", id=string.uuid())),
    )


@pytest.fixture()
def headers(jwt_token: str) -> dict[str, str]:
    return {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Bearer {0}".format(jwt_token),
    }


@pytest.fixture()
def app(  # noqa: WPS211
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    redis_repository: UserSessionRepository,
    transactions_client: transactions.Client,
    companies_client: companies.Client,
    conversions_repository: pay_repos.ConversionRepository,
    cc_payment_client: PaymentClient,
) -> applications.Starlette:
    return _create_app(
        payment_client=cc_payment_client,
        currencies_client=currencies_client,
        quotations_client=quotations_client,
        redis_repository=redis_repository,
        conversion_repository=conversions_repository,
        transactions_client=transactions_client,
        companies_client=companies_client,
        openapi_path=filesystem.resource_path("junction.pay_api", "openapi.json"),
    )


@pytest.fixture()
def admin_app(  # noqa: WPS211
    authentication_client: auth.Client,
    cc_payment_client: PaymentClient,
    accounts_client: accounts.GrpcClient,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    payment_client: payments.GrpcClient,
    conversions_repository: pay_repos.ConversionRepository,
    transactions_client: transactions.Client,
    conversions_client: conversions.Client,
    currencies_client: currencies.Client,
    beneficiaries_client: beneficiaries.Client,
    refunds_client: refunds.Client,
    custom_middlewares: Sequence[Middleware],
) -> applications.Starlette:
    return _create_admin_app(
        cc_payment_client=cc_payment_client,
        authentication_client=authentication_client,
        accounts_client=accounts_client,
        companies_client=companies_client,
        contacts_client=contacts_client,
        payment_client=payment_client,
        conversions_repository=conversions_repository,
        transactions_client=transactions_client,
        conversions_client=conversions_client,
        currencies_client=currencies_client,
        beneficiaries_client=beneficiaries_client,
        refunds_client=refunds_client,
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
