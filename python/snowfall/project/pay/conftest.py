from collections.abc import Sequence

import pytest

from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter import currencies, payments
from snowfall.stdlib import money


@pytest.fixture()
def available_currencies() -> Sequence[money.Currency]:
    return (
        money.Currency("USD"),
        money.Currency("GBP"),
        money.Currency("AMD"),
        money.Currency("SEK"),
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
def payments_client() -> payments.Client:
    return payments.DictClient(fixtures.get_payments())
