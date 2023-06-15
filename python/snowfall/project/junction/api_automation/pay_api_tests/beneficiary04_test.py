import json
import logging

import httpx
import pytest

from snowfall.project.junction.api_automation.pay_api_tests.conftest import (
    PAY_TEST_ACCOUNT01,
    PAY_TEST_ACCOUNT02,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger_test = logging.getLogger()
logger_test.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_update_beneficiary(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="GBP test Account Holder",
            email="example@example.com",
            beneficiary_address_lines=[
                "Radhuset",
                "Våksalagatan 2",
                "United Spaces",
                "Sweden",
            ],
            beneficiary_country_code="GB",
            bank_name="mBank S.A.",
            account_type="checking",
            payment_types="priority",
            bank_address_lines=[
                "mBank S.A.",
                "Bankowość detaliczna",
                "Skrytka Pocztowa 2108",
                "90-959",
                "Łódź 2",
            ],
            bank_country_code="GB",
            currency_id="GBP",
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban="GB89370400440532013000",
        )
    except httpx.HTTPStatusError as err:
        logger_test.info("response_create_beneficiary err: %s", err.response.headers)
        logger_test.info("response_create_beneficiary body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    update_bank_account_holder_name = "EUR test Account Holder for update beneficiary"
    update_email = "example1@example.com"
    update_beneficiary_address_lines = [
        "Radhuseu",
        "Våksalagatan 3",
        "United Spacet",
        "Swedeo",
    ]
    update_beneficiary_country_code = "DE"
    update_bank_name = "mBank S.B."
    update_account_type = "savings"
    update_payment_types = "regular"
    update_bank_address_lines = [
        "mBank S.B.",
        "Bankowość detalicznb",
        "Skrytka Pocztowa 2109",
        "90-950",
        "Łódź 3",
    ]
    update_bank_country_code = "DE"
    update_currency_id = "EUR"
    update_account_id = PAY_TEST_ACCOUNT02
    update_beneficiary_postal_code = "12346"
    update_beneficiary_city = "Uppsalb"
    update_bic_swift = "BREXPLPWMBL"
    update_iban = "DE89370400440532013001"

    try:
        response_update_beneficiary = await pay_admin_client.update_beneficiary(
            beneficiary_id=response_create_beneficiary["data"]["id"],
            bank_account_holder_name=update_bank_account_holder_name,
            email=update_email,
            beneficiary_address_lines=update_beneficiary_address_lines,
            beneficiary_country_code=update_beneficiary_country_code,
            bank_name=update_bank_name,
            account_type=update_account_type,
            payment_types=update_payment_types,
            bank_address_lines=update_bank_address_lines,
            bank_country_code=update_bank_country_code,
            currency_id=update_currency_id,
            account_id=update_account_id,
            beneficiary_postal_code=update_beneficiary_postal_code,
            beneficiary_city=update_beneficiary_city,
            bic_swift=update_bic_swift,
            iban=update_iban,
        )
    except httpx.HTTPStatusError as err2:
        logger_test.info("response_update_beneficiary err: %s", err2.response.headers)
        logger_test.info("response_update_beneficiary body: %s", err2.response.json())
        pytest.fail(err2.response.json(), pytrace=False)

    logger_test.info(
        "update_beneficiary: %s",
        json.dumps(response_update_beneficiary, indent=4),
    )

    rub_data = response_update_beneficiary["data"]
    assert (
        rub_data["attributes"]["bankAccountHolderName"]
        == update_bank_account_holder_name
    )
    assert rub_data["attributes"]["email"] == update_email
    assert rub_data["attributes"]["beneficiaryAddress"]["addressLines"] == [
        " ".join(update_beneficiary_address_lines),
    ]
    assert (
        rub_data["attributes"]["beneficiaryAddress"]["countryCode"]
        == update_beneficiary_country_code
    )
    assert (
        rub_data["attributes"]["beneficiaryAddress"]["postalCode"]
        == update_beneficiary_postal_code
    )
    assert (
        rub_data["attributes"]["beneficiaryAddress"]["city"] == update_beneficiary_city
    )
    assert rub_data["attributes"]["beneficiaryAddress"]["state"] is None
    assert rub_data["attributes"]["bankDetails"]["name"] == update_bank_name
    assert rub_data["attributes"]["bankDetails"]["bicSwift"] == update_bic_swift
    assert rub_data["attributes"]["bankDetails"]["accountType"] == update_account_type
    assert rub_data["attributes"]["bankDetails"]["paymentTypes"] == update_payment_types
    assert (
        rub_data["attributes"]["bankDetails"]["address"]["addressLines"]
        == update_bank_address_lines
    )
    assert (
        rub_data["attributes"]["bankDetails"]["address"]["countryCode"]
        == update_bank_country_code
    )
    assert rub_data["attributes"]["bankDetails"]["accountNumber"] == update_iban
    assert rub_data["attributes"]["bankDetails"]["aba"] is None
    assert rub_data["relationships"]["currency"]["data"]["id"] == update_currency_id
    assert rub_data["relationships"]["account"]["data"]["id"] == update_account_id
    assert "https" in response_update_beneficiary["links"]["self"]
