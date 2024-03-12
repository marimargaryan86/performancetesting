import secrets
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from unittest import mock

import httpx
import pytest
from google.protobuf import struct_pb2
from motor import core
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.adapter import identities
from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, orders, resellers
from snowfall.project.junction.hub.service.hub_api import (
    bootstrap,
    permissions,
    repository,
    router,
)
from snowfall.project.junction.hub.service.hub_api.v1 import (
    models_pb2 as hub_models_pb2,
)
from snowfall.project.junction.plus.adapter import (
    configuration_vectors as config_vector_adapter,
)
from snowfall.project.junction.plus.service.notifications.v1 import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import (
    bills,
    companies,
    contacts,
    credit_card_payment,
    currencies,
    quotations,
    refunds,
    transactions,
)
from snowfall.project.pay.service.transactions.v1.models_pb2 import (
    Bill,
    Quotation,
    QuotationAmounts,
    QuotationRates,
)
from snowfall.service.authentication.v1 import identities_pb2
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib import money, string
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem

RESELLER_ID = "effb6d65-2ddc-4a26-9b57-af79d44254cb"
IDENTITIY_IDS = (
    "37b82d2f-dba3-469e-9076-12b15777d1f5",
    "dc33945e-40b9-4227-ae9a-81c68a3a592a",
)


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(
        identifier="foo",
        email="foo@example.com",
        metadata={
            "role": "snowfall-admin",
        },
    )


async def mock_cookie_to_reseller_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(
        identifier="foo",
        email="foo@example.com",
        metadata={
            "reseller_id": RESELLER_ID,
            "role": "reseller-admin",
        },
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Cookie": "ory_kratos_session='test_cookie_header'",
    }


@pytest.fixture()
def orders_client() -> orders.Client:
    return orders.DictClient(
        fixtures.get_journeys(),
        fixtures.get_cancellation_requests(),
    )


def _generate_identity(
    identifier: str,
    reseller_id: str | None = None,
) -> identities_pb2.Identity:
    metadata_public = struct_pb2.Struct()
    if reseller_id:
        metadata_public.update({"role": "reseller-admin", "reseller_id": reseller_id})
    else:
        metadata_public.update({"role": "snowfall-admin"})
    return identities_pb2.Identity(
        id=identifier,
        email="foobar@example.com",
        metadata_public=metadata_public,
    )


@pytest.fixture()
def ory_identities() -> Sequence[identities_pb2.Identity]:
    return [
        _generate_identity(IDENTITIY_IDS[0], RESELLER_ID),
        _generate_identity(IDENTITIY_IDS[1]),
    ]


@pytest.fixture()
def identities_client(
    ory_identities: Sequence[identities_pb2.Identity],
) -> identities.Client:
    return identities.DictClient(ory_identities)


@pytest.fixture()
def companies_client() -> companies.Client:
    return companies.DictClient(
        pay_fixtures.get_companies(),
    )


@pytest.fixture()
def currencies_client(
    available_currencies: Sequence[money.Currency],
) -> currencies.DictClient:
    return currencies.DictClient(
        {
            ("USD", "EUR"): 0.95,
            ("EUR", "USD"): 1.05,
        },
        available_currencies,
    )


@pytest.fixture()
def refunds_client(cc_payment_client: mock.Mock) -> refunds.DictClient:
    refund_data = [
        pay_fixtures.generate_refund(refund_id) for refund_id in pay_fixtures.REFUNDS
    ]
    return refunds.DictClient(
        refund_data,
        [
            pay_fixtures.generate_transaction(refund.transaction_id)
            for refund in refund_data
        ],
        cc_payment_client,
    )


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
def transactions_client(
    transaction_ids: Sequence[str],
) -> transactions.Client:
    return transactions.DictClient(
        [
            pay_fixtures.generate_transaction(transaction_id)
            for transaction_id in transaction_ids
        ],
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


def get_bill(bill_id: str) -> Bill:
    money_usd = money.from_string("1000", money.Currency("USD")).protobuf()
    return Bill(
        id=bill_id,
        order_id=string.uuid(),
        is_reconciled=False,
        total_amount=money_usd,
    )


@pytest.fixture()
def cc_payment_client() -> mock.Mock:
    payment_client = mock.Mock()

    detailed_rate = mock.Mock()
    detailed_rate.client_buy_amount = secrets.randbelow(9999) + 1  # noqa: WPS432
    payment_client.get_detailed_rates = mock.AsyncMock(
        return_value=detailed_rate,
    )

    return payment_client


@pytest.fixture()
def bad_contacts_client() -> contacts.DictClient:
    return contacts.DictClient(
        [
            pay_fixtures.generate_contact(pay_fixtures.CONTACTS[0]),
            pay_fixtures.generate_contact_with_bad_company_id(pay_fixtures.CONTACTS[1]),
        ],
    )


@pytest.fixture()
def contacts_client() -> contacts.DictClient:
    return contacts.DictClient(
        [
            pay_fixtures.generate_contact(pay_fixtures.CONTACTS[0]),
        ],
    )


@pytest.fixture()
def quotations_client(
    quotations_ids: Sequence[str],
) -> quotations.Client:
    return quotations.DictClient(
        [get_quotation(quotations_id) for quotations_id in quotations_ids],
    )


@pytest.fixture()
def bills_client() -> bills.Client:
    return bills.DictClient(
        [get_bill(bill_id) for bill_id in pay_fixtures.BILLS],
    )


@pytest.fixture()
def resellers_client() -> resellers.Client:
    return resellers.DictClient(fixtures.get_resellers())


@pytest.fixture()
def credit_card_payment_client() -> credit_card_payment.Client:
    return credit_card_payment.DictClient()


@pytest.fixture()
async def user() -> hub_models_pb2.User:
    return hub_models_pb2.User(
        id=string.uuid(),
        ory_identity_id=IDENTITIY_IDS[0],
        reseller_id=RESELLER_ID,
    )


@pytest.fixture()
async def users_repository(
    mongo_client: core.AgnosticClient,
    user: hub_models_pb2.User,
) -> repository.UsersRepository:
    users_repository = repository.UsersRepository(
        collection=mongo_client.test.users,
    )

    await users_repository.insert(user)

    return users_repository


def _create_app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    identities_client: identities.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
    credit_card_payment_client: credit_card_payment.Client,
    config_vector_client: config_vector_adapter.Client,
    users_repository: repository.UsersRepository,
    cookie_to_user: Callable[[str], Awaitable[stdlib_auth.User]],
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                orders_client=orders_client,
                companies_client=companies_client,
                contacts_client=contacts_client,
                identities_client=identities_client,
                transactions_client=transactions_client,
                currencies_client=currencies_client,
                quotations_client=quotations_client,
                bills_client=bills_client,
                refunds_client=refunds_client,
                resellers_client=resellers_client,
                credit_card_payment_client=credit_card_payment_client,
                config_vectors_client=config_vector_client,
                users_repository=users_repository,
            ),
        ),
        openapi_path=filesystem.resource_path("junction.hub_api", "openapi.json"),
        custom_middlewares=[
            middleware.Middleware(
                auth_middleware.AuthenticationMiddleware,
                backend=authentication.CookieAuthenticationBackend(
                    cookie_to_user=cookie_to_user,
                ),
                on_error=handlers.auth_error_handler,
            ),
            middleware.Middleware(permissions.PermissionsMiddleware),
        ],
        security_headers=False,
    )

    asgi_app.add_exception_handler(
        errors.NotFoundError,
        handlers.not_found_error_handler,
    )
    asgi_app.add_exception_handler(
        errors.UnprocessableEntityError,
        handlers.unprocessable_entity_error_handler,
    )

    return asgi_app


@pytest.fixture()
async def client(
    app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
async def users_client(
    users_app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=users_app,
        base_url="https://example.com",
    ) as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
async def config_vector_client() -> config_vector_adapter.Client:
    return config_vector_adapter.DictClient(
        configuration_vectors=[
            notifications_models_pb2.ConfigurationVector(
                id="649d74da91449640d4db8357",
                reseller_id="04f83af5-10bb-4a0f-1881-03e1e690f0f5",
                email="test@example.com",
                search_url="https://test_url",
                permissions=["flight_stats_alerts", "whatsapp_chatbot"],
            ),
        ],
    )


@pytest.fixture()
def app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    bad_contacts_client: contacts.Client,
    identities_client: identities.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
    credit_card_payment_client: credit_card_payment.Client,
    config_vector_client: config_vector_adapter.Client,
    users_repository: repository.UsersRepository,
) -> applications.Starlette:
    return _create_app(
        orders_client=orders_client,
        companies_client=companies_client,
        contacts_client=bad_contacts_client,
        transactions_client=transactions_client,
        identities_client=identities_client,
        currencies_client=currencies_client,
        quotations_client=quotations_client,
        bills_client=bills_client,
        refunds_client=refunds_client,
        resellers_client=resellers_client,
        credit_card_payment_client=credit_card_payment_client,
        config_vector_client=config_vector_client,
        users_repository=users_repository,
        cookie_to_user=mock_cookie_to_user,
    )


@pytest.fixture()
def users_app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    identities_client: identities.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
    credit_card_payment_client: credit_card_payment.Client,
    config_vector_client: config_vector_adapter.Client,
    users_repository: repository.UsersRepository,
) -> applications.Starlette:
    return _create_app(
        orders_client=orders_client,
        companies_client=companies_client,
        contacts_client=contacts_client,
        transactions_client=transactions_client,
        currencies_client=currencies_client,
        identities_client=identities_client,
        quotations_client=quotations_client,
        bills_client=bills_client,
        refunds_client=refunds_client,
        resellers_client=resellers_client,
        credit_card_payment_client=credit_card_payment_client,
        config_vector_client=config_vector_client,
        users_repository=users_repository,
        cookie_to_user=mock_cookie_to_reseller_user,
    )
