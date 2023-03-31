import logging

import pytest

from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models import exchange

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_quote(
    api_layer_client: APILayer,
) -> None:
    buy_currency = "USD"
    sell_currency = "EUR"
    amount = 1.23

    response = await api_layer_client.quote(buy_currency, sell_currency, amount)
    logging.info("quote: %s", response)

    assert response == exchange.Quote(
        amount=int(amount),
        buy_currency=buy_currency,
        sell_currency=sell_currency,
        rate=response.rate,
    )
