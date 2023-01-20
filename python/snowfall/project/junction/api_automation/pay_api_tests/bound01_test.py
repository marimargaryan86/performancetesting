import logging

import pytest

from snowfall.vendor.apilayer.models import exchange
from snowfall.vendor.bound.client import Bound

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration
async def test_quote(
    bound_client: Bound,
) -> None:
    buy_currency = "USD"
    sell_currency = "EUR"
    amount = 1.23

    response = await bound_client.quote(buy_currency, sell_currency, amount)
    logging.info("quote: %s", response)

    assert response == exchange.Quote(
        amount=int(amount),
        buy_currency=buy_currency,
        sell_currency=sell_currency,
        rate=response.rate,
    )


@pytest.mark.integration
async def test_get_rates(
    bound_client: Bound,
) -> None:
    currency_pair = "USDEUR"

    response = await bound_client.get_rates(currency_pair)
    logging.info("get_rates: %s", response)

    assert response[0] == exchange.Rate(
        buy_currency=currency_pair[:3],
        sell_currency=currency_pair[3:],
        rate=response[0].rate,
    )
