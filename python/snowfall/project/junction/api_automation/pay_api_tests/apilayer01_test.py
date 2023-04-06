import logging
import random

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import (
    EXIT_MSG,
    expected_currencies_list,
)
from snowfall.vendor.apilayer.client import APILayer
from snowfall.vendor.apilayer.models import exchange

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_quote(
    api_layer_client: APILayer,
) -> None:
    buy_currency, sell_currency = random.sample(expected_currencies_list, 2)

    amount = 1.23
    try:
        response = await api_layer_client.quote(buy_currency, sell_currency, amount)
    except httpx.HTTPStatusError as err:
        logger.info("response api_layer quote err: %s", err.response.headers)
        logger.info("response api_layer quote body: %s", err.response.json())
        pytest.exit(EXIT_MSG)

    logging.info("quote: %s", response)

    assert response == exchange.Quote(
        amount=int(amount),
        buy_currency=buy_currency,
        sell_currency=sell_currency,
        rate=response.rate,
    )
