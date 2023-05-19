import json
import logging

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_list_beneficiaries(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    try:
        response_list_beneficiaries = await pay_admin_client.list_beneficiaries()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_beneficiaries err: %s", err.response.headers)
        logger.info("response_list_beneficiaries body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info(
        "list_beneficiaries: %s",
        json.dumps(response_list_beneficiaries, indent=4),
    )
    first_item = response_list_beneficiaries["data"][0]
    assert is_valid_uuid(first_item["id"])
    assert first_item["type"] == "beneficiaries"
    assert isinstance(first_item["attributes"]["bankAccountHolderName"], str)
    assert isinstance(first_item["attributes"]["email"], str)
    assert isinstance(
        first_item["attributes"]["beneficiaryAddress"]["addressLines"],
        list,
    )
    assert isinstance(
        first_item["attributes"]["beneficiaryAddress"]["countryCode"],
        str,
    )
    assert isinstance(first_item["attributes"]["beneficiaryAddress"]["postalCode"], str)
    assert isinstance(first_item["attributes"]["beneficiaryAddress"]["city"], str)
    assert isinstance(
        first_item["attributes"]["beneficiaryAddress"]["state"],
        type(None) | str,
    )
    assert isinstance(first_item["attributes"]["bankDetails"]["iban"], str)
    assert isinstance(first_item["attributes"]["bankDetails"]["name"], str)
    assert isinstance(
        first_item["attributes"]["bankDetails"]["bicSwift"],
        type(None) | str,
    )
    assert first_item["attributes"]["bankDetails"]["accountType"], (
        "checking" or "savings"
    )
    assert (
        first_item["attributes"]["bankDetails"]["paymentTypes"] == "priority"
        or "regular"
    )
    assert isinstance(
        first_item["attributes"]["bankDetails"]["address"]["addressLines"],
        list,
    )
    assert isinstance(
        first_item["attributes"]["bankDetails"]["address"]["countryCode"],
        str,
    )

    assert isinstance(first_item["relationships"]["currency"]["data"]["id"], str)
    assert first_item["relationships"]["currency"]["data"]["type"] == "currencies"
    assert isinstance(first_item["relationships"]["account"]["data"]["id"], str)
    assert first_item["relationships"]["account"]["data"]["type"] == "accounts"

    assert "https" in first_item["links"]["self"]
    assert "https" in response_list_beneficiaries["links"]["next"]
