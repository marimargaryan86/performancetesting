import json
import logging
from typing import Any, Mapping

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
async def test_get_beneficiary(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_list_beneficiaries: Mapping[str, Any],
) -> None:
    beneficiary_id = pay_list_beneficiaries["data"][0]["id"]

    try:
        response_get_beneficiary = await pay_admin_client.get_beneficiary(
            beneficiary_id,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_get_beneficiary err: %s", err.response.headers)
        logger.info("response_get_beneficiary body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)

    logger.info(
        "get_beneficiary: %s",
        json.dumps(response_get_beneficiary, indent=4),
    )
    rgb_data = response_get_beneficiary["data"]

    assert is_valid_uuid(rgb_data["id"])
    assert rgb_data["type"] == "beneficiaries"
    assert isinstance(
        rgb_data["attributes"]["bankAccountHolderName"],
        str,
    )
    assert isinstance(rgb_data["attributes"]["email"], str)
    assert isinstance(
        rgb_data["attributes"]["beneficiaryAddress"]["addressLines"],
        list,
    )
    assert isinstance(
        rgb_data["attributes"]["beneficiaryAddress"]["countryCode"],
        str,
    )
    assert isinstance(
        rgb_data["attributes"]["beneficiaryAddress"]["postalCode"],
        str,
    )
    assert isinstance(
        rgb_data["attributes"]["beneficiaryAddress"]["city"],
        str,
    )
    assert isinstance(
        rgb_data["attributes"]["beneficiaryAddress"]["state"],
        type(None) | str,
    )
    assert isinstance(
        rgb_data["attributes"]["bankDetails"]["iban"],
        str,
    )
    assert isinstance(
        rgb_data["attributes"]["bankDetails"]["name"],
        str,
    )
    assert isinstance(
        rgb_data["attributes"]["bankDetails"]["bicSwift"],
        type(None) | str,
    )
    assert rgb_data["attributes"]["bankDetails"]["accountType"], "checking" or "savings"
    assert (
        rgb_data["attributes"]["bankDetails"]["paymentTypes"] == "priority" or "regular"
    )
    assert isinstance(
        rgb_data["attributes"]["bankDetails"]["address"]["addressLines"],
        list,
    )
    assert isinstance(
        rgb_data["attributes"]["bankDetails"]["address"]["countryCode"],
        str,
    )

    assert isinstance(
        rgb_data["relationships"]["currency"]["data"]["id"],
        str,
    )
    assert rgb_data["relationships"]["currency"]["data"]["type"] == "currencies"
    assert isinstance(
        rgb_data["relationships"]["account"]["data"]["id"],
        str,
    )
    assert rgb_data["relationships"]["account"]["data"]["type"] == "accounts"

    assert "https" in rgb_data["links"]["self"]
