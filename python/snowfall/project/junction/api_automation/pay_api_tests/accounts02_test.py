import json
import logging
import sys
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.vendor.pay.client import PayAdminClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_create_account(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_create_contact_persons: Mapping[str, Any],
) -> None:
    name = "test account {0}".format(return_randomized_token())
    try:
        response_create_account = await pay_admin_client.create_accounts(
            name,
            pay_create_contact_persons["data"]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_account: %s", err.response.headers)
        logger.info("response_create_account body: %s", err.response.json())
        sys.exit(EXIT_MSG)
    logger.info(
        "response_create_account: %s",
        json.dumps(response_create_account, indent=4),
    )

    assert is_valid_uuid(response_create_account["data"]["id"])
    assert response_create_account["data"]["type"] == "accounts"
    assert isinstance(response_create_account["data"]["attributes"]["name"], str)
    assert isinstance(response_create_account["data"]["attributes"]["status"], str)
    relationships = response_create_account["data"]["relationships"]
    assert is_valid_uuid(relationships["company"]["data"]["id"])
    assert relationships["company"]["data"]["type"] == "companies"
    assert is_valid_uuid(relationships["contactPerson"]["data"]["id"])
    assert relationships["contactPerson"]["data"]["type"] == "contact-persons"
