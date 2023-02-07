import json
import logging
import sys

import pytest
from dateutil import parser

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_client import (
    PayApiClient,
)
from snowfall.stdlib import string

logger = logging.getLogger()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
se = logging.StreamHandler(sys.stderr)
se.setFormatter(formatter)
logger.addHandler(se)
logger.setLevel(logging.DEBUG)


@pytest.mark.integration
async def test_create_transactions(  # noqa: WPS218, WPS210
    pay_client: PayApiClient,
) -> None:
    response_payer = await pay_client.create_company(
        company="test-company-{0}".format(return_randomized_token()),
        address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
        country_code="SE",
        postal_code="75320",
        city="Uppsala",
        buffer_rate=float(0),
        sales_rate=float(0),
    )

    response_beneficiary = await pay_client.create_company(
        company="test-company-{0}".format(return_randomized_token()),
        address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
        country_code="SE",
        postal_code="75320",
        city="Uppsala",
        buffer_rate=float(0),
        sales_rate=float(0),
    )

    response_create_quote = await pay_client.create_quote(
        amount=1000,
        payer_id=response_payer["data"]["id"],
        beneficiary_id=response_beneficiary["data"]["id"],
        from_currency="USD",
        to_currency="EUR",
    )
    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    parent_external_reference = string.uuid()
    response = await pay_client.create_transactions(
        external_reference=external_reference,
        parent_external_reference=parent_external_reference,
        quotation_id=response_create_quote["data"]["id"],
    )
    logger.info("create_transactions: %s", json.dumps(response, indent=4))

    quotation = response["data"]["relationships"]["quotation"]["data"]

    assert (
        is_valid_uuid(response["data"]["id"]) is True
    ), "transactions uuid must be in valid format"
    assert response["data"]["type"] == "transactions"
    assert response["data"]["attributes"]["externalReference"] == external_reference
    assert (
        response["data"]["attributes"]["parentExternalReference"]
        == parent_external_reference
    )
    try:
        is_valid_date = bool(parser.parse(response["data"]["attributes"]["createdAt"]))
    except parser.ParserError:
        is_valid_date = False
    assert is_valid_date
    assert quotation["id"] == response_create_quote["data"]["id"]
    assert quotation["type"] == "quotations"
