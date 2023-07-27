import datetime
from collections.abc import Sequence
from unittest import mock

import pytest

from snowfall.project.pay.adapter import accounts, quotations
from snowfall.project.pay.service.companies.v1alpha.models_pb2 import (
    Account,
    Company,
    Status,
)
from snowfall.project.pay.service.conversions.v1alpha.models_pb2 import Conversion
from snowfall.project.pay.service.pay_api.repositories import ConversionRepository
from snowfall.project.pay.service.transactions.v1alpha.models_pb2 import (
    Quotation,
    QuotationStatus,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1 import postal_address_pb2
from snowfall.vendor.currency_cloud.models.balance import BalanceResponse


@pytest.fixture()
async def quote_is_less_than_the_limit(
    quotations_client: quotations.Client,
    valid_company: Company,
) -> Quotation:
    usd = money.Money(8, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    return await quotations_client.create(
        from_currency=gbp.currency.code,
        to_currency=usd.currency.code,
        amount=8,
        payer=valid_company,
        beneficiary_company=valid_company,
        session_token=string.uuid(),
        tax=8,
    )


@pytest.fixture()
async def booked_quote(
    quotations_client: quotations.Client,
    valid_company: Company,
) -> Quotation:
    usd = money.Money(1, money.Currency("USD"))
    gbp = money.Money(1, money.Currency("GBP"))
    quote = await quotations_client.create(
        from_currency=gbp.currency.code,
        to_currency=usd.currency.code,
        amount=8,
        payer=valid_company,
        beneficiary_company=valid_company,
        session_token=string.uuid(),
        tax=8,
    )
    await quotations_client.update_status(
        quote.id,
        QuotationStatus.QUOTATION_STATUS_CONFIRMED,
    )

    return await quotations_client.get(quote.id)


@pytest.fixture()
async def booked_quote_quoted(
    quotations_client: quotations.Client,
    valid_company: Company,
) -> Quotation:
    usd = money.Money(8, money.Currency("USD"))
    gbp = money.Money(4, money.Currency("GBP"))
    return await quotations_client.create(
        from_currency=gbp.currency.code,
        to_currency=usd.currency.code,
        amount=8,
        payer=valid_company,
        beneficiary_company=valid_company,
        session_token=string.uuid(),
        tax=8,
    )


@pytest.fixture()
async def valid_conversion(
    conversions_repository: ConversionRepository,
) -> Conversion:
    usd = money.Money(100, money.Currency("USD"))
    gbp = money.Money(100, money.Currency("GBP"))

    conversion = Conversion(
        id="ed7b9b96-6c5a-4a6b-adee-2af14564e42b",
        external_id="f8144974-530f-477f-bbe1-c2eaedddec88",
        settlement_date=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=1),
        ),
        created_at=protobuf.datetime_to_protobuf(
            datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=2),
        ),
        buy_amount=usd.protobuf(),
        sell_amount=gbp.protobuf(),
        executed_rate=1,
    )

    return await conversions_repository.insert(conversion)


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
async def accounts_based_on_cc_accounts(
    accounts_client: accounts.DictClient,
    accounts_list_from_cc: Sequence[mock.Mock],
) -> list[Account]:
    return [
        await accounts_client.create(
            Account(
                id=string.uuid(),
                external_reference=account.identifier,
                contact_id=string.uuid(),
                company_id=string.uuid(),
                name="Snowfall",
                status=protobuf.slug_to_enum_value(
                    Status,
                    "enabled",
                ),
            ),
        )
        for account in accounts_list_from_cc
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
async def account(
    accounts_client: accounts.DictClient,
    balance: BalanceResponse,
) -> Account:
    return await accounts_client.create(
        Account(
            id=balance.account_id,
            external_reference=string.uuid(),
            company_id="9b4a1e83-a0e9-49b3-aa79-fccb6add617c",
            contact_id="8304c0ff-7ba6-4431-9788-1d486be3a033",
        ),
    )


@pytest.fixture()
async def valid_company() -> Company:
    return Company(
        id="ed7b9b96-6c5a-4a6b-adee-2af14564e42b",
        name="Company",
        address=postal_address_pb2.PostalAddress(
            address_lines=["Street name 7"],
            region_code="GB",
            postal_code="12345",
            locality="London",
        ),
        fx_markup=float(1),
        processing_markup=float(1),
        sales_markup=float(1),
    )


@pytest.fixture()
async def company(
    account: Account,
) -> Company:
    fx_markup = 1.2
    processing_markup = 2.2
    sales_markup = 2.3

    return Company(
        id=account.company_id,
        name="test_company",
        fx_markup=fx_markup,
        processing_markup=processing_markup,
        sales_markup=sales_markup,
        account_id=account.id,
    )
