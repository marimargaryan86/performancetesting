import pytest

from snowfall.project.junction.rocket.provider import parsers
from snowfall.project.junction.rocket.service.searches.v1alpha import models_pb2
from snowfall.stdlib import money


@pytest.mark.parametrize(
    ("base_fare", "tax_amount", "currency"),
    [
        ("29.50", "15.50", "USD"),
        ("13.37", "49.33", "SEK"),
        ("6.66", "14.68", "GBP"),
        ("334", "666", "JPY"),
    ],
)
def test_parse_price_breakdown(  # noqa: WPS218
    base_fare: str,
    tax_amount: str,
    currency: str,
) -> None:
    price_breakdown = parsers.parse_price_breakdown(base_fare, tax_amount, currency)

    base_fare_breakdown = price_breakdown[0]
    base_fare_price = money.from_protobuf(base_fare_breakdown.price)
    assert str(base_fare_price) == base_fare
    assert base_fare_price.currency.code == currency
    assert (
        base_fare_breakdown.breakdown_type
        == models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )

    tax_breakdown = price_breakdown[1]
    tax_price = money.from_protobuf(tax_breakdown.price)
    assert str(tax_price) == tax_amount
    assert tax_price.currency.code == currency
    assert tax_breakdown.breakdown_type == models_pb2.PriceBreakdown.BREAKDOWN_TYPE_TAX


def test_parse_price_breakdown_no_tax() -> None:
    price_breakdown = parsers.parse_price_breakdown("50.00", None, "EUR")

    assert len(price_breakdown) == 1

    base_fare_breakdown = price_breakdown[0]
    base_fare_price = money.from_protobuf(base_fare_breakdown.price)
    assert str(base_fare_price) == "50.00"
    assert base_fare_price.currency.code == "EUR"
    assert (
        base_fare_breakdown.breakdown_type
        == models_pb2.PriceBreakdown.BREAKDOWN_TYPE_BASE_FARE
    )
