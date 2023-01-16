import pytest

from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.quotations.quote_calculations import Quote
from snowfall.stdlib import money


@pytest.fixture
def company() -> company_models.Company:
    return company_models.Company(
        name="Snowfall",
        sales_rate=0.06,
        buffer_rate=0.01,
    )


async def test_same_currencies(
    company: company_models.Company,
) -> None:
    expected_amount = money.Money(10600, money.Currency("USD"))

    quote = Quote(
        10000,
        money.Currency("USD"),
        money.Currency("USD"),
        1.0,
        company,
        "beneficiary_id",
    ).to_proto()

    assert money.from_protobuf(quote.offer_amount).amount == expected_amount.amount


async def test_calculation(
    company: company_models.Company,
) -> None:
    expected_offer_amount = money.Money(11770, money.Currency("USD"))
    expected_sales_amount = money.Money(660, money.Currency("USD"))
    expected_buffer_amount = money.Money(110, money.Currency("USD"))

    quote = Quote(
        10000,
        money.Currency("EUR"),
        money.Currency("USD"),
        1.1,
        company,
        "beneficiary_id",
    ).to_proto()

    assert (
        money.from_protobuf(quote.sales_amount).amount == expected_sales_amount.amount
    )
    assert (
        money.from_protobuf(quote.buffer_amount).amount == expected_buffer_amount.amount
    )
    assert (
        money.from_protobuf(quote.offer_amount).amount == expected_offer_amount.amount
    )
