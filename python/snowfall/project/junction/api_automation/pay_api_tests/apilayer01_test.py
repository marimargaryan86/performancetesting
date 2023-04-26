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
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info("quote: %s", response)

    logger.info(
        "exchange.Quote: %s",
        exchange.Quote(
            amount=int(amount * response.rate),
            buy_currency=buy_currency,
            sell_currency=sell_currency,
            rate=response.rate,
        ),
    )

    assert response == exchange.Quote(
        amount=int(amount * response.rate),
        buy_currency=buy_currency,
        sell_currency=sell_currency,
        rate=response.rate,
    )
