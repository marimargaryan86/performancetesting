import json
import logging

import httpx
import pytest
from dateutil import parser

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
@pytest.mark.parametrize(
    ("from_currency", "to_currency"),
    [("EUR", "SEK"), ("EUR", "EUR")],
)
async def test_create_transactions(  # noqa: WPS210, WPS213, WPS218, C901
    pay_client: Client,
    pay_admin_client: PayAdminClient,
    from_currency: str,
    to_currency: str,
) -> None:
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
        logger.info(
            "response_create_quote err:: %s",
            err2.response.headers,
        )
        logger.info("response_create_quote body: %s", err2.response.json())
        pytest.fail(err2.response.json(), pytrace=False)

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
        pytest.fail(err3.response.json(), pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    rct_data = response_create_transactions["data"]

    assert (
        is_valid_uuid(rct_data["id"]) is True
    ), "transactions uuid must be in valid format"
    assert rct_data["type"] == "transactions"
    assert rct_data["attributes"]["externalReference"] == external_reference
    assert rct_data["attributes"]["invoiceReference"] == invoice_reference
    try:
        is_valid_date = bool(
            parser.parse(
                rct_data["attributes"]["createdAt"],
            ),
        )
    except parser.ParserError:
        is_valid_date = False
    assert is_valid_date
    assert isinstance(
        rct_data["attributes"]["amounts"]["beneficiary"]["currency"],
        str,
    )
    assert isinstance(rct_data["attributes"]["amounts"]["beneficiary"]["amount"], int)
    assert isinstance(rct_data["attributes"]["amounts"]["quotation"]["currency"], str)
    assert isinstance(rct_data["attributes"]["amounts"]["quotation"]["amount"], int)
    assert isinstance(
        rct_data["attributes"]["amounts"]["baseConverted"]["currency"],
        str,
    )
    assert isinstance(
        rct_data["attributes"]["amounts"]["baseConverted"]["amount"],
        int,
    )
    assert isinstance(
        rct_data["attributes"]["amounts"]["salesMargin"]["currency"],
        str,
    )
    assert isinstance(rct_data["attributes"]["amounts"]["salesMargin"]["amount"], int)
    assert isinstance(rct_data["attributes"]["amounts"]["fxMargin"]["currency"], str)
    assert isinstance(rct_data["attributes"]["amounts"]["fxMargin"]["amount"], int)
    assert isinstance(
        rct_data["attributes"]["amounts"]["processingMargin"]["currency"],
        str,
    )
    assert isinstance(
        rct_data["attributes"]["amounts"]["processingMargin"]["amount"],
        int,
    )
    assert isinstance(rct_data["attributes"]["rates"]["fxQuote"], float)
    assert isinstance(rct_data["attributes"]["rates"]["fxBuffer"], float)
    assert isinstance(rct_data["attributes"]["rates"]["salesMarkup"], float)
    assert isinstance(rct_data["attributes"]["rates"]["fxMarkup"], float)
    assert isinstance(rct_data["attributes"]["rates"]["processingMarkup"], float)
    if from_currency == to_currency:
        assert rct_data["relationships"]["conversion"] is None
    else:
        assert is_valid_uuid(rct_data["relationships"]["conversion"]["data"]["id"])
        assert rct_data["relationships"]["conversion"]["data"]["type"] == "conversions"
    assert is_valid_uuid(rct_data["relationships"]["payer"]["data"]["id"])
    assert rct_data["relationships"]["payer"]["data"]["type"] == "companies"
    assert is_valid_uuid(rct_data["relationships"]["beneficiary"]["data"]["id"])
    assert rct_data["relationships"]["beneficiary"]["data"]["type"] == "companies"
