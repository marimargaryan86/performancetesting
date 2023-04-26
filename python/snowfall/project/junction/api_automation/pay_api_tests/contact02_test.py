import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import EXIT_MSG
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.mark.integration()
async def test_list_contacts(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
    pay_create_contact: Mapping[str, Any],
) -> None:
    contact_id = pay_create_contact["data"]["id"]
    first_name = pay_create_contact["data"]["attributes"]["firstName"]
    last_name = pay_create_contact["data"]["attributes"]["lastName"]
    email_address = pay_create_contact["data"]["attributes"]["emailAddress"]
    phone_number = pay_create_contact["data"]["attributes"]["phoneNumber"]
    pay_create_contact_relationships = pay_create_contact["data"]["relationships"]
    company_id = pay_create_contact_relationships["company"]["data"]["id"]

    try:
        rlc = await pay_admin_client.list_contacts(company_id)
    except httpx.HTTPStatusError as err:
        logger.info("response_list_contacts err: %s", err.response.headers)
        logger.info("response_list_contacts body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "list_contacts: %s",
        json.dumps(rlc, indent=4),
    )

    assert is_valid_uuid(rlc["data"][0]["id"])
    assert rlc["data"][0]["id"] == contact_id
    assert rlc["data"][0]["type"] == "contacts"
    assert rlc["data"][0]["attributes"]["firstName"] == first_name
    assert rlc["data"][0]["attributes"]["lastName"] == last_name
    assert rlc["data"][0]["attributes"]["emailAddress"] == email_address
    assert rlc["data"][0]["attributes"]["phoneNumber"] == phone_number
    relationships = rlc["data"][0]["relationships"]
    assert is_valid_uuid(relationships["company"]["data"]["id"])
    assert relationships["company"]["data"]["type"] == "companies"
