import json
import logging

import httpx
import pytest

from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.rate import BasicRateResponse

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_get_basic_rates(
    payment_test_client: PaymentClient,
) -> None:
    try:
        response_get_basic_rates = await payment_test_client.get_basic_rates("USDEUR")
    except httpx.HTTPStatusError as err:
        logger.info("response_get_basic_rates err: %s", err.response.headers)
        logger.info("response_get_basic_rates body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info(
        "get_basic_rates: %s",
        response_get_basic_rates,
    )

    assert isinstance(response_get_basic_rates[0], BasicRateResponse)
    basic_rate_response = json.loads(response_get_basic_rates[0].json())
    assert basic_rate_response["buy_currency"] == "EUR"
    assert basic_rate_response["sell_currency"] == "USD"
    assert isinstance(basic_rate_response["rate"], float)
