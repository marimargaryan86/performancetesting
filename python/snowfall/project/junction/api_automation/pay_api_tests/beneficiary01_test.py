import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from snowfall.project.junction.api_automation.pay_api_tests.conftest import (
    PAY_TEST_ACCOUNT01,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_create_beneficiary_usd(  # noqa: WPS210
    pay_admin_client: PayAdminClient,
) -> None:
    aba = "122228634"
    iban = None
    state = "California"
    account_number = "61109010140000071"
    currency = "USD"
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="USD test Account Holder",
            email="example@example.com",
            account_number=account_number,
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
            currency_id=currency,
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            beneficiary_state=state,
            bic_swift="BREXPLPWMBK",
            aba=aba,
            iban=iban,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_beneficiary_usd: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )
    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        aba,
        iban,
        state,
        currency,
        account_number,
        is_beneficiary_state=True,
        is_aba=True,
        is_iban=False,
    )


@pytest.mark.integration()
async def test_create_beneficiary_eur(  # noqa: WPS210
    pay_admin_client: PayAdminClient,
) -> None:
    aba = None
    iban = "DE89370400440532013000"
    state = None
    currency = "EUR"
    account_number = None
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
            currency_id=currency,
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban=iban,
            aba=aba,
            beneficiary_state=state,
            account_number=account_number,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )

    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        aba,
        iban,
        state,
        currency,
        account_number,
        is_beneficiary_state=False,
        is_aba=False,
        is_iban=True,
    )


@pytest.mark.integration()
async def test_create_beneficiary_gbp(  # noqa: WPS210
    pay_admin_client: PayAdminClient,
) -> None:
    aba = None
    iban = "GB89370400440532013000"
    state = None
    currency = "GBP"
    account_number = None
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
            currency_id=currency,
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban=iban,
            aba=aba,
            beneficiary_state=state,
            account_number=account_number,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )

    execute_response_create_beneficiary_assertions(
        response_create_beneficiary,
        aba,
        iban,
        state,
        currency,
        account_number,
        is_beneficiary_state=False,
        is_aba=False,
        is_iban=True,
    )


def execute_response_create_beneficiary_assertions(  # noqa: WPS218
    response: Mapping[str, Any],
    aba: str | None,
    iban: str | None,
    state: str | None,
    currency: str,
    account_number: str | None,
    is_beneficiary_state: bool = True,
    is_aba: bool = True,
    is_iban: bool = True,
) -> None:
    rd = response["data"]
    if is_beneficiary_state:
        assert rd["attributes"]["beneficiaryAddress"]["state"] == state
    else:
        assert rd["attributes"]["beneficiaryAddress"]["state"] is None
    if is_aba:
        assert rd["attributes"]["bankDetails"]["aba"] == aba
        assert rd["attributes"]["bankDetails"]["accountNumber"] == account_number
    else:
        assert rd["attributes"]["bankDetails"].get("aba") is None
        assert rd["attributes"]["bankDetails"].get("accountNumber") is None
    if is_iban:
        assert rd["attributes"]["bankDetails"]["iban"] == iban
    else:
        assert rd["attributes"]["bankDetails"].get("iban") is None

    assert rd["relationships"]["currency"]["data"]["id"] == currency
