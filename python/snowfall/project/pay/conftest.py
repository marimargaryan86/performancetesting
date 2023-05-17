import pytest

from snowfall.project.pay.adapter import currencies


@pytest.fixture()
def currencies_client() -> currencies.Client:
    return currencies.DictClient(
        {
            ("USD", "EUR"): 0.95,
            ("EUR", "USD"): 1.05,
        },
    )
