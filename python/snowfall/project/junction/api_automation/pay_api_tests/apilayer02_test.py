import logging
import random

import pytest

from snowfall.project.junction.api_automation.conftest import expected_currencies_list
from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models import exchange

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_rate(
    api_layer_client: APILayer,
) -> None:
    buy_currency, sell_currency = random.sample(expected_currencies_list, 2)

    response = await api_layer_client.get_rates(
        source=sell_currency,
        currencies=buy_currency,
    )
    rate_splitted = str(response).split("rate=")
    rate_string = rate_splitted[1][:-2]
    logging.info("get_rates: %s", response)
    assert response == [
        exchange.Rate(
            buy_currency=buy_currency,
            sell_currency=sell_currency,
            rate=float(rate_string),
        ),
    ]
