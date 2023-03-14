import json
import logging
import sys
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.vendor.pay.client import PayAdminClient

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_get_accounts(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_create_account: Mapping[str, Any],
) -> None:
    try:
        response_get_accounts = await pay_admin_client.get_accounts()
    except httpx.HTTPStatusError as err:
        logger.info("response_get_accounts err: %s", err.response.headers)
        logger.info("response_get_accounts body: %s", err.response.json())
        sys.exit(EXIT_MSG)

    logger.info("get_accounts: %s", json.dumps(response_get_accounts, indent=4))
    first_entry = response_get_accounts["data"][0]
    assert is_valid_uuid(first_entry["id"])
    assert first_entry["type"] == "accounts"
    assert isinstance(first_entry["attributes"]["name"], str)
    assert isinstance(first_entry["attributes"]["status"], str)
    assert is_valid_uuid(first_entry["relationships"]["company"]["data"]["id"])
    assert first_entry["relationships"]["company"]["data"]["type"] == "companies"
    assert is_valid_uuid(first_entry["relationships"]["contactPerson"]["data"]["id"])
    assert (
        first_entry["relationships"]["contactPerson"]["data"]["type"]
        == "contact-persons"
    )
