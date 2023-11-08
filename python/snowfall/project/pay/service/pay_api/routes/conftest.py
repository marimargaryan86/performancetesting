from collections.abc import Sequence

import pytest

from snowfall.project.pay.adapter import quotations
from snowfall.project.pay.service.companies.v1.models_pb2 import (
    Company,
)
from snowfall.project.pay.service.transactions.v1.models_pb2 import (
    Quotation,
    QuotationStatus,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.v1 import postal_address_pb2


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
