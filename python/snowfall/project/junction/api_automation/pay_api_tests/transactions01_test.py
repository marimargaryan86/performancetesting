import json
import logging
from typing import Any, Mapping

import httpx
import pytest
from dateutil import parser

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
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
async def test_create_transactions(  # noqa: WPS210, WPS213, C901
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    get_mongo_config: Mapping[str, Any],
) -> None:
    try:
        response_payer = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float(0),
            fx_provider_markup=float(0),
            sales_markup=float(0),
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
            fx_markup=float(0),
            fx_provider_markup=float(0),
            sales_markup=float(0),
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
            "response_create_quote err:: %s",
            err2.response.headers,
        )
        logger.info("response_create_quote body: %s", err2.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    logger.info("external_reference: %s", external_reference)
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

    assert (
        is_valid_uuid(response_create_transactions["data"]["id"]) is True
    ), "transactions uuid must be in valid format"
    assert response_create_transactions["data"]["type"] == "transactions"
    assert (
        response_create_transactions["data"]["attributes"]["externalReference"]
        == external_reference
    )
    assert (
        response_create_transactions["data"]["attributes"]["invoiceReference"]
        == invoice_reference
    )
    try:
        is_valid_date = bool(
            parser.parse(
                response_create_transactions["data"]["attributes"]["createdAt"],
            ),
        )
    except parser.ParserError:
        is_valid_date = False
    assert is_valid_date
