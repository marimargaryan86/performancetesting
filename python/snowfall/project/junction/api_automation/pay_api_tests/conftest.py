import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.stdlib import string
from snowfall.vendor.junction.pay.client import Client as PayClient

logger = logging.getLogger()


@pytest.fixture()
async def pay_create_account(
    pay_admin_client: PayAdminClient,
    pay_create_contact: Mapping[str, Any],
) -> dict[str, Any]:
    name = "test account {0}".format(return_randomized_token())
    try:
        response_create_account = await pay_admin_client.create_accounts(
            name,
            pay_create_contact["data"]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_account: %s", err.response.headers)
        logger.info("response_create_account body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info(
        "response_create_account: %s",
        json.dumps(response_create_account, indent=4),
    )
    return response_create_account


@pytest.fixture()
async def pay_create_transaction(  # noqa: WPS210, WPS213, C901
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    float0 = float(0)
    try:
        response_payer = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float0,
            fx_provider_markup=float0,
            sales_markup=float0,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_payer err: %s", err.response.headers)
        logger.info("response_payer body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    try:
        response_beneficiary = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float0,
            fx_provider_markup=float0,
            sales_markup=float0,
        )
    except httpx.HTTPStatusError as err1:
        logger.info("response_beneficiary err:: %s", err1.response.headers)
        logger.info("response_beneficiary body: %s", err1.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=response_payer["data"]["id"],
            beneficiary_id=response_beneficiary["data"]["id"],
            from_currency="EUR",
            to_currency="SEK",
        )
    except httpx.HTTPStatusError as err2:
        logger.info(
            "response_create_quote err: %s",
            err2.response.headers,
        )
        logger.info("response_create_quote body: %s", err2.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    logger.info(": %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", response_create_quote["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=response_create_quote["data"]["id"],
        )

    except httpx.HTTPStatusError as err3:
        logger.info("response err:: %s", err3.response.headers)
        logger.info("response_create_transactions body: %s", err3.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    return response_create_transactions
