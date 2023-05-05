import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.pay_api_tests.conftest import (
    PAY_TEST_ACCOUNT01,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_beneficiary_usd(
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="USD test Account Holder",
            email="example@example.com",
            account_number="61109010140000071",
            beneficiary_address_lines=[
                "Radhuset",
                "Våksalagatan 2",
                "United Spaces",
                "Sweden",
            ],
            beneficiary_country_code="US",
            bank_name="mBank S.A.",
            account_type="checking",
            payment_types="priority",
            bank_address_lines=[
                "mBank S.A.",
                "Bankowość detaliczna",
                "Skrytka Pocztowa 2108",
                "90- 959",
                "Łódź 2",
            ],
            bank_country_code="US",
            currency_id="USD",
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            beneficiary_state="California",
            bic_swift="BREXPLPWMBK",
            aba="122228634",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "create_beneficiary_usd: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )
    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        "USD",
        is_beneficiary_state=True,
        is_aba=True,
        is_iban=False,
    )


@pytest.mark.integration()
async def test_create_beneficiary_eur(
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="EUR test Account Holder",
            email="example@example.com",
            beneficiary_address_lines=[
                "Radhuset",
                "Våksalagatan 2",
                "United Spaces",
                "Sweden",
            ],
            beneficiary_country_code="DE",
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
            bank_country_code="DE",
            currency_id="EUR",
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban="DE89370400440532013000",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )

    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        "EUR",
        is_beneficiary_state=False,
        is_aba=False,
        is_iban=True,
    )


@pytest.mark.integration()
async def test_create_beneficiary_gbp(
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
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )

    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        "GBP",
        is_beneficiary_state=False,
        is_aba=False,
        is_iban=True,
    )


def execute_response_create_beneficiary_assertions(  # noqa: WPS218
    response: Mapping[str, Any],
    currency: str,
    is_beneficiary_state: bool = True,
    is_aba: bool = True,
    is_iban: bool = True,
) -> None:
    rd = response["data"]
    assert is_valid_uuid(rd["id"])
    assert rd["type"] == "beneficiaries"
    assert isinstance(rd["attributes"]["bankAccountHolderName"], str)
    assert isinstance(rd["attributes"]["email"], str)
    assert isinstance(
        rd["attributes"]["beneficiaryAddress"]["addressLines"],
        list,
    )
    assert isinstance(
        rd["attributes"]["beneficiaryAddress"]["countryCode"],
        str,
    )
    assert isinstance(
        rd["attributes"]["beneficiaryAddress"]["postalCode"],
        str,
    )
    assert isinstance(rd["attributes"]["beneficiaryAddress"]["city"], str)
    if is_beneficiary_state:
        assert isinstance(
            rd["attributes"]["beneficiaryAddress"]["state"],
            str,
        )
    else:
        assert rd["attributes"]["beneficiaryAddress"]["state"] is None

    assert isinstance(rd["attributes"]["bankDetails"]["name"], str)
    assert isinstance(rd["attributes"]["bankDetails"]["bicSwift"], str)
    if is_aba:
        assert isinstance(rd["attributes"]["bankDetails"]["aba"], str)
        assert isinstance(rd["attributes"]["bankDetails"]["accountNumber"], str)
    else:
        assert rd["attributes"]["bankDetails"].get("aba") is None
        assert rd["attributes"]["bankDetails"].get("accountNumber") is None
    if is_iban:
        assert isinstance(rd["attributes"]["bankDetails"]["iban"], str)
    else:
        assert rd["attributes"]["bankDetails"].get("iban") is None
    assert isinstance(rd["attributes"]["bankDetails"]["accountType"], str)
    assert isinstance(
        rd["attributes"]["bankDetails"]["paymentTypes"],
        str,
    )
    assert isinstance(rd["attributes"]["bankDetails"]["name"], str)

    assert isinstance(
        rd["attributes"]["bankDetails"]["address"]["addressLines"],
        list,
    )
    assert isinstance(
        rd["attributes"]["bankDetails"]["address"]["countryCode"],
        str,
    )

    assert rd["relationships"]["currency"]["data"]["id"] == currency
    assert rd["relationships"]["currency"]["data"]["type"] == "currencies"
    assert is_valid_uuid(rd["relationships"]["account"]["data"]["id"])
    assert rd["relationships"]["account"]["data"]["type"] == "accounts"

    assert isinstance(
        rd["attributes"]["bankDetails"]["address"]["addressLines"],
        list,
    )
    assert isinstance(
        rd["attributes"]["bankDetails"]["address"]["countryCode"],
        str,
    )
