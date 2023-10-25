import secrets
from collections.abc import AsyncIterator, Mapping, Sequence
from unittest import mock

import httpx
import pytest
from starlette import applications, middleware
from starlette.middleware import authentication as auth_middleware

from snowfall.project.junction.go import fixtures
from snowfall.project.junction.go.adapter import errors, orders, resellers
from snowfall.project.junction.hub.service.hub_api import bootstrap, permissions, router
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import (
    accounts,
    beneficiaries,
    bills,
    companies,
    contacts,
    conversions,
    currencies,
    quotations,
    refunds,
    transactions,
)
from snowfall.project.pay.service.companies.v1alpha import models_pb2
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import (
    Bill,
    Quotation,
    QuotationAmounts,
    QuotationRates,
    Transaction,
)
from snowfall.stdlib import authentication as stdlib_auth
from snowfall.stdlib import money, string
from snowfall.stdlib.integration.starlette import application, authentication, handlers
from snowfall.stdlib.persistence import filesystem
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse
from snowfall.vendor.currency_cloud.models.beneficiary import BeneficiaryResponse


async def mock_cookie_to_user(cookie: str) -> stdlib_auth.User:
    return stdlib_auth.User(
        identifier="foo",
        email="foo@example.com",
        metadata={"reseller_id": "mock", "role": "snowfall-admin"},
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


@pytest.fixture()
def companies_client() -> companies.Client:
    return companies.DictClient(
        pay_fixtures.get_companies(),
    )


@pytest.fixture()
def beneficiaries_client() -> beneficiaries.DictClient:
    return beneficiaries.DictClient(
        (
            models_pb2.Beneficiary(
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
def conversions_client(
    transaction_ids: Sequence[str],
) -> conversions.DictClient:
    return conversions.DictClient(
        [
            pay_fixtures.generate_conversion(conversion_id)
            for conversion_id in pay_fixtures.CONVERSIONS
        ],
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
        [get_transaction(refund.transaction_id) for refund in refund_data],
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


@pytest.fixture()
def transactions_client(
    transaction_ids: Sequence[str],
) -> transactions.Client:
    return transactions.DictClient(
        [get_transaction(transaction_id) for transaction_id in transaction_ids],
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
    detailed_rate.client_buy_amount = secrets.randbelow(9999) + 1  # noqa: WPS432
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


def _create_app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    accounts_client: accounts.Client,
    contacts_client: contacts.Client,
    beneficiaries_client: beneficiaries.Client,
    conversions_client: conversions.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    cc_payment_client: PaymentClient,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
) -> applications.Starlette:
    asgi_app = application.create_starlette_app(
        routes=router.get_routes(
            bootstrap.create_dependencies(
                orders_client=orders_client,
                companies_client=companies_client,
                accounts_client=accounts_client,
                contacts_client=contacts_client,
                beneficiaries_client=beneficiaries_client,
                conversions_client=conversions_client,
                transactions_client=transactions_client,
                currencies_client=currencies_client,
                cc_payment_client=cc_payment_client,
                quotations_client=quotations_client,
                bills_client=bills_client,
                refunds_client=refunds_client,
                resellers_client=resellers_client,
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
    async with httpx.AsyncClient(app=app, base_url="https://example.com") as client:
        client.headers.update(dict(headers))

        yield client


@pytest.fixture()
def app(
    orders_client: orders.Client,
    companies_client: companies.Client,
    contacts_client: contacts.Client,
    accounts_client: accounts.Client,
    conversions_client: conversions.Client,
    beneficiaries_client: beneficiaries.Client,
    transactions_client: transactions.Client,
    currencies_client: currencies.Client,
    cc_payment_client: PaymentClient,
    quotations_client: quotations.Client,
    bills_client: bills.Client,
    refunds_client: refunds.Client,
    resellers_client: resellers.Client,
) -> applications.Starlette:
    return _create_app(
        orders_client=orders_client,
        companies_client=companies_client,
        contacts_client=contacts_client,
        accounts_client=accounts_client,
        conversions_client=conversions_client,
        beneficiaries_client=beneficiaries_client,
        transactions_client=transactions_client,
        currencies_client=currencies_client,
        cc_payment_client=cc_payment_client,
        quotations_client=quotations_client,
        bills_client=bills_client,
        refunds_client=refunds_client,
        resellers_client=resellers_client,
    )
