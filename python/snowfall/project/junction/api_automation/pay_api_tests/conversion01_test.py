import datetime
import json
import logging
import sys
from typing import Any, Mapping

import httpx
import pytest
from dateutil.parser import parse as datetime_parse

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.stdlib import string
from snowfall.vendor.pay.client import PayAdminClient, PayClient

logger = logging.getLogger()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
se = logging.StreamHandler(sys.stderr)
se.setFormatter(formatter)
logger.addHandler(se)
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_get_conversion_details(  # noqa: WPS210, WPS213, C901
    pay_client: PayClient,
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
            buffer_rate=float(0),
            sales_rate=float(0),
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_payer err: %s", err.response.headers)
        logger.info("response_payer body: %s", err.response.json())
        sys.exit(EXIT_MSG)

    try:
        response_beneficiary = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            buffer_rate=float(0),
            sales_rate=float(0),
        )
    except httpx.HTTPStatusError as err1:
        logger.info("response_beneficiary err:: %s", err1.response.headers)
        logger.info("response_beneficiary body: %s", err1.response.json())
        sys.exit(EXIT_MSG)

    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
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
        sys.exit(EXIT_MSG)

    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    logger.info("external_reference: %s", external_reference)
    parent_external_reference = string.uuid()
    logger.info("parent_external_reference: %s", parent_external_reference)
    logger.info("quotation_id: %s", response_create_quote["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            parent_external_reference=parent_external_reference,
            quotation_id=response_create_quote["data"]["id"],
        )

    except httpx.HTTPStatusError as err3:
        logger.info("response err:: %s", err3.response.headers)
        logger.info("response_create_transactions body: %s", err3.response.json())
        sys.exit(EXIT_MSG)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    conversion = response_create_transactions["data"]["relationships"]["conversion"][
        "data"
    ]
    conversion_id = conversion["id"]
    response = await pay_admin_client.get_conversion_details(
        conversion_id,
    )

    assert response["data"]["id"] == conversion_id
    assert is_valid_uuid(response["data"]["id"])
    assert response["data"]["type"] == "conversions"
    assert isinstance(response["data"]["attributes"]["rate"], float)
    assert isinstance(
        datetime_parse(
            response["data"]["attributes"]["settledAt"],
        ),
        datetime.date,
    )
