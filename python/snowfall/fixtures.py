import types

from snowfall.stdlib import money

LATITUDE_RANGE = (-90, 90)
LONGITUDE_RANGE = (-180, 180)

NOT_FOUND = "00000000-0000-0000-0000-000000000000"

_CURRENCIES_CONVERSIONS = types.MappingProxyType(
    {
        ("USD", "EUR"): 0.95,
        ("EUR", "USD"): 1.05,
    },
)
CURRENCIES = (money.Currency("USD"), money.Currency("EUR"))


def get_currencies() -> types.MappingProxyType[tuple[str, str], float]:
    return _CURRENCIES_CONVERSIONS
