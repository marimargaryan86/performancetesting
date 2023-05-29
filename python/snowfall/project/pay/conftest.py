import pytest

from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter import currencies, payments


@pytest.fixture()
def currencies_client() -> currencies.Client:
    return currencies.DictClient(
        {
            ("USD", "EUR"): 0.95,
            ("EUR", "USD"): 1.05,
        },
    )


@pytest.fixture()
def payments_client() -> payments.Client:
    return payments.DictClient(fixtures.get_payments())
