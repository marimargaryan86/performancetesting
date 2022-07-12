import pytest

from snowfall.stdlib import money


@pytest.mark.parametrize(
    "amount,currency,string_value",
    [
        (1550, "USD", "15.50"),
        (1337, "SEK", "13.37"),
        (666, "GBP", "6.66"),
        (666, "JPY", "666"),
        (666, "JOD", "0.666"),
        (-175, "USD", "-1.75"),
    ],
)
def test_to_and_from_string(amount: int, currency: str, string_value: str) -> None:
    currency_obj = money.Currency(currency)
    instance = money.Money(amount, currency_obj)

    assert str(instance) == string_value
    assert money.from_string(string_value, currency_obj) == instance


@pytest.mark.parametrize(
    "amount,currency,string_value,separator",
    [
        (450, "EUR", "4.5", "."),
        (-450, "EUR", "-4.5", "."),
        (400, "EUR", "4.", "."),
        (457, "EUR", "4.567", "."),
        (15, "JPY", "15.00", "."),
        (15, "JPY", "15.49", "."),
        (16, "JPY", "15.50", "."),
        (16, "JPY", "15,50", ","),
    ],
)
def test_from_string(
    amount: int,
    currency: str,
    string_value: str,
    separator: str,
) -> None:
    currency_obj = money.Currency(currency)
    instance = money.Money(amount, currency_obj)

    assert money.from_string(string_value, currency_obj, separator) == instance


@pytest.mark.parametrize(
    "amount,currency,units,nanos",
    [
        (1550, "USD", 15, 500000000),
        (1337, "SEK", 13, 370000000),
        (666, "GBP", 6, 660000000),
        (666, "JPY", 666, 0),
        (666, "JOD", 0, 666000000),
        (-175, "USD", -1, -750000000),
    ],
)
def test_to_and_from_protobuf(
    amount: int,
    currency: str,
    units: int,
    nanos: int,
) -> None:
    instance = money.Money(amount, money.Currency(currency))
    proto = instance.protobuf()

    assert proto.currency_code == currency
    assert proto.units == units
    assert proto.nanos == nanos
    assert money.from_protobuf(proto) == instance


@pytest.mark.parametrize(
    "amount,amount2,expected",
    [
        (175, 175, 350),
        (175, -175, 0),
        (-175, -175, -350),
    ],
)
def test_add(amount: int, amount2: int, expected: int) -> None:
    currency = money.Currency("USD")
    instance = money.Money(amount, currency)
    instance2 = money.Money(amount2, currency)

    assert instance.add(instance2).amount == expected


def test_add_with_different_currencies() -> None:
    instance = money.Money(175, money.Currency("USD"))
    instance2 = money.Money(175, money.Currency("SEK"))

    with pytest.raises(RuntimeError):
        instance.add(instance2)
