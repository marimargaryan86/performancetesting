import pytest

from snowfall.project.pay.service.companies.v1 import models_pb2 as company_models
from snowfall.project.pay.service.transactions.quote import Quote
from snowfall.stdlib import money


@pytest.fixture()
def company() -> company_models.Company:
    return company_models.Company(
        name="Snowfall",
        fx_markup=0.4,
        processing_markup=0.2,
        sales_markup=float(1),
        fee_amounts=[
            money.Money(200, money.Currency("GBP")).protobuf(),  # noqa: WPS432
            money.Money(100, money.Currency("EUR")).protobuf(),  # noqa: WPS432
        ],
        apply_markups=True,
        vertical_fees=[
            company_models.VerticalFee(
                vertical_type=company_models.VerticalType.VERTICAL_TYPE_RAIL,
                value=1.0,
                billing_type=company_models.BillingType.BILLING_TYPE_FIXED,
            ),
            company_models.VerticalFee(
                vertical_type=company_models.VerticalType.VERTICAL_TYPE_AIR,
                value=0.5,
                billing_type=company_models.BillingType.BILLING_TYPE_PERCENTAGE,
            ),
        ],
    )


@pytest.fixture()
def company_without_margins() -> company_models.Company:
    return company_models.Company(
        name="Snowfall",
        fx_markup=0.4,
        processing_markup=0.2,
        sales_markup=float(1),
        apply_markups=False,
    )


async def test_same_currencies(
    company: company_models.Company,
) -> None:
    expected_amount = money.Money(101200, money.Currency("USD"))

    quote = Quote(
        100000,
        money.Currency("USD"),
        money.Currency("USD"),
        1,
        company,
        "beneficiary_id",
        0,
        2,
        company_models.VerticalType.VERTICAL_TYPE_RAIL,
    ).to_proto()

    assert money.from_protobuf(quote.amounts.quotation).amount == expected_amount.amount


async def test_calculation(  # noqa: WPS218
    company: company_models.Company,
) -> None:
    expected_amounts = {
        "quotation": money.Money(117856, money.Currency("EUR")).amount,
        "sales_margin": money.Money(1160, money.Currency("EUR")).amount,
        "base_converted": money.Money(116000, money.Currency("EUR")).amount,
        "fx_margin": money.Money(464, money.Currency("EUR")).amount,
        "processing_margin": money.Money(232, money.Currency("EUR")).amount,
        "service_markup": money.Money(1856, money.Currency("EUR")).amount,
        "total_markups": money.Money(2188, money.Currency("EUR")).amount,
    }

    quote = Quote(
        100000,
        money.Currency("GBP"),
        money.Currency("EUR"),
        1.16,
        company,
        "beneficiary_id",
        0,
        2,
        company_models.VerticalType.VERTICAL_TYPE_RAIL,
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
        money.from_protobuf(quote.amounts.processing_margin).amount
        == expected_amounts["processing_margin"]
    )
    assert (
        money.from_protobuf(quote.amounts.service_markup).amount
        == expected_amounts["service_markup"]
    )
    assert (
        money.from_protobuf(quote.amounts.total_markups).amount
        == expected_amounts["total_markups"]
    )


async def test_calculation_without_margins(  # noqa: WPS218
    company_without_margins: company_models.Company,
) -> None:
    expected_amounts = {
        "base_converted": money.Money(116000, money.Currency("EUR")).amount,
        "service_markup": money.Money(0, money.Currency("EUR")).amount,
        "total_markups": money.Money(0, money.Currency("EUR")).amount,
    }

    quote = Quote(
        100000,
        money.Currency("GBP"),
        money.Currency("EUR"),
        1.16,
        company_without_margins,
        "beneficiary_id",
        0,
        2,
        company_models.VerticalType.VERTICAL_TYPE_RAIL,
    ).to_proto()

    assert (
        money.from_protobuf(quote.amounts.base_converted).amount
        == expected_amounts["base_converted"]
    )
    assert (
        money.from_protobuf(quote.amounts.service_markup).amount
        == expected_amounts["service_markup"]
    )
    assert (
        money.from_protobuf(quote.amounts.total_markups).amount
        == expected_amounts["total_markups"]
    )


async def test_percentage_vertical(
    company: company_models.Company,
) -> None:
    total_markups = money.Money(2668, money.Currency("EUR")).amount

    quote = Quote(
        100000,
        money.Currency("GBP"),
        money.Currency("EUR"),
        1.16,
        company,
        "beneficiary_id",
        0,
        2,
        company_models.VerticalType.VERTICAL_TYPE_AIR,
    ).to_proto()

    assert money.from_protobuf(quote.amounts.total_markups).amount == total_markups
