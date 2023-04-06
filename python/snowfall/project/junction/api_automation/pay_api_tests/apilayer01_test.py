import logging
import random

import pytest

from snowfall.project.junction.api_automation.conftest import expected_currencies_list
from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models import exchange

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_quote(
    api_layer_client: APILayer,
) -> None:
    buy_currency, sell_currency = random.sample(expected_currencies_list, 2)

    amount = 1.23

    response = await api_layer_client.quote(buy_currency, sell_currency, amount)
    logging.info("quote: %s", response)

    assert response == exchange.Quote(
        amount=int(amount),
        buy_currency=buy_currency,
        sell_currency=sell_currency,
        rate=response.rate,
    )
