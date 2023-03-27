import pytest

from snowfall.project.pay.service.companies.v1alpha import models_pb2 as company_models
from snowfall.project.pay.service.quotations.quote_calculations import Quote
from snowfall.stdlib import money


@pytest.fixture
def company() -> company_models.Company:
    return company_models.Company(
        name="Snowfall",
        fx_markup=float(0.4),
        fx_provider_markup=float(0.2),
        sales_markup=float(1),
    )


async def test_same_currencies(
    company: company_models.Company,
) -> None:
    expected_amount = money.Money(101000, money.Currency("USD"))

    quote = Quote(
        100000,
        money.Currency("USD"),
        money.Currency("USD"),
        1,
        company,
        "beneficiary_id",
    ).to_proto()

    assert money.from_protobuf(quote.amounts.quotation).amount == expected_amount.amount


async def test_calculation(
    company: company_models.Company,
) -> None:
    expected_amounts = {
        "quotation": money.Money(117856, money.Currency("EUR")).amount,
        "sales_margin": money.Money(1160, money.Currency("EUR")).amount,
        "base_converted": money.Money(116000, money.Currency("EUR")).amount,
        "fx_margin": money.Money(464, money.Currency("EUR")).amount,
        "fx_provider_margin": money.Money(232, money.Currency("EUR")).amount,
    }

    quote = Quote(
        100000,
        money.Currency("GBP"),
        money.Currency("EUR"),
        1.16,
        company,
        "beneficiary_id",
    ).to_proto()

    assert (
        money.from_protobuf(quote.amounts.quotation).amount
        == expected_amounts["quotation"]
    )
    assert (
        money.from_protobuf(quote.amounts.sales_margin).amount
        == expected_amounts["sales_margin"]
    )
    assert (
        money.from_protobuf(quote.amounts.base_converted).amount
        == expected_amounts["base_converted"]
    )
    assert (
        money.from_protobuf(quote.amounts.fx_margin).amount
        == expected_amounts["fx_margin"]
    )
    assert (
        money.from_protobuf(quote.amounts.fx_provider_margin).amount
        == expected_amounts["fx_provider_margin"]
    )
