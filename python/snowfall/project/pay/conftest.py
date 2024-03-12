from collections.abc import Sequence

import pytest

from snowfall.project.pay.adapter import currencies
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
