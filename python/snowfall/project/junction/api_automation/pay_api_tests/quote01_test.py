import json
import logging
import random

import httpx
import pytest

from snowfall.project.junction.api_automation.pay_api_tests.conftest import (
    expected_currencies_list,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.stdlib import string
from snowfall.vendor.junction.pay.client import Client

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_quote(  # noqa: WPS210, WPS213
    pay_admin_client: PayAdminClient,
    pay_client: Client,
) -> None:
    from_currency, to_currency = random.sample(expected_currencies_list, 2)

    try:
        response_payer = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float(0),
            processing_markup=float(0),
            sales_markup=float(0),
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_payer err: %s", err.response.headers)
        logger.info("response_payer body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    try:
        response_beneficiary = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float(0),
            processing_markup=float(0),
            sales_markup=float(0),
        )
    except httpx.HTTPStatusError as err1:
        logger.info("response_beneficiary err:: %s", err1.response.headers)
        logger.info("response_beneficiary body: %s", err1.response.json())
        pytest.fail(err1.response.json(), pytrace=False)

    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=response_payer["data"]["id"],
            beneficiary_id=response_beneficiary["data"]["id"],
            from_currency=from_currency,
            to_currency=to_currency,
        )
    except httpx.HTTPStatusError as err2:
        logger.info("response_beneficiary err:: %s", err2.response.headers)
        logger.info("response_beneficiary body: %s", err2.response.json())
        pytest.fail(err2.response.json(), pytrace=False)

    logging.info("quote: %s", json.dumps(response_create_quote, indent=4))

    relationships = response_create_quote["data"]["relationships"]

    assert relationships["fromCurrency"]["data"]["id"] == from_currency
    assert relationships["toCurrency"]["data"]["id"] == to_currency
    assert relationships["payer"]["data"]["id"] == response_payer["data"]["id"]
    assert (
        relationships["beneficiary"]["data"]["id"] == response_beneficiary["data"]["id"]
    )
