import random
from collections.abc import AsyncIterator, Mapping, Sequence
from unittest import mock

import httpx
import pytest
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, orders
from snowfall.project.junction.hub.service.hub_api import bootstrap, router
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import accounts, companies, contacts
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse
from snowfall.vendor.currency_cloud.models.beneficiary import BeneficiaryResponse


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(identifier="foo", email="foo@example.com")


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
        fixtures.get_bookings_cancellations(),
    )


@pytest.fixture()
def companies_client() -> companies.Client:
    return companies.DictClient(
        pay_fixtures.get_companies(),
    )


@pytest.fixture()
def accounts_list_from_cc() -> list[mock.Mock]:
    return [
        mock.Mock(
            account_name="Snowfall",
            legal_entity_type="company",
            street="10-12 East Parade",
            city="Leeds",
            country="GB",
            postal_code="LS1 2BH",
            state_or_province="",
            spread_table="flat_0.00",
            api_trading=True,
            online_trading=True,
            phone_trading=True,
            terms_and_conditions_accepted=None,
            identifier="9954f733-27a8-46e5-9bf8-28b7b43ecd87",
            status="enabled",
        ),
        mock.Mock(
            account_name="Junction Pay First Account",
            legal_entity_type="company",
            street="1 Arcacia Avenue",
            city="Tiddlington",
            country="GB",
            postal_code="OX1 1FX",
            state_or_province="Oxfordshire",
            spread_table="fxcg_rfx_default",
            api_trading=True,
            online_trading=True,
            phone_trading=True,
            terms_and_conditions_accepted=None,
            identifier="6c37ed2c-6494-4d94-9c85-ff8e15e719ea",
            status="enabled",
        ),
    ]


@pytest.fixture()
def balance() -> BalanceResponse:
    return BalanceResponse(
        amount="10",
        currency="USD",
        identifier=string.uuid(),
        account_id=string.uuid(),
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
def accounts_client() -> accounts.DictClient:
    return accounts.DictClient()


@pytest.fixture()
def contacts_client() -> contacts.DictClient:
    return contacts.DictClient(
        [
            pay_fixtures.generate_contact(pay_fixtures.CONTACTS[0]),
            pay_fixtures.generate_contact_with_bad_company_id(pay_fixtures.CONTACTS[1]),
        ],
    )


def _create_app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    accounts_client: accounts.Client,
    cc_payment_client: PaymentClient,
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                orders_client=orders_client,
                companies_client=companies_client,
                accounts_client=accounts_client,
                contacts_client=contacts_client,
                cc_payment_client=cc_payment_client,
            ),
        ),
        openapi_path=filesystem.resource_path("junction.hub_api", "openapi.json"),
        custom_middlewares=[
            middleware.Middleware(
                auth_middleware.AuthenticationMiddleware,
                backend=authentication.CookieAuthenticationBackend(
                    cookie_to_user=mock_cookie_to_user,
                ),
                on_error=handlers.auth_error_handler,
            ),
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
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
def app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    accounts_client: accounts.Client,
    cc_payment_client: PaymentClient,
) -> applications.Starlette:
    return _create_app(
        orders_client=orders_client,
        companies_client=companies_client,
        accounts_client=accounts_client,
        contacts_client=contacts_client,
        cc_payment_client=cc_payment_client,
    )
