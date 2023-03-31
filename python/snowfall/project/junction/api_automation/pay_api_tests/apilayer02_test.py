import logging

import pytest

from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models import exchange

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_get_rate(
    api_layer_client: APILayer,
) -> None:
    source = "USD"
    currencies = "EUR"

    response = await api_layer_client.get_rates(
        source=source,
        currencies=currencies,
    )
    rate_splitted = str(response).split("rate=")
    rate_string = rate_splitted[1][:-2]
    logging.info("get_rates: %s", response)
    assert response == [
        exchange.Rate(
            buy_currency=currencies,
            sell_currency=source,
            rate=float(rate_string),
        ),
    ]
