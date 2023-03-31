import json
import logging
import sys

import httpx
import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logger = logging.getLogger()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
se = logging.StreamHandler(sys.stderr)
se.setFormatter(formatter)
logger.addHandler(se)
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration()
async def test_create_contacts(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    company = "test-company-{0}".format(return_randomized_token())
    address_lines = ["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"]
    country_code = "SE"
    postal_code = "75320"
    city = "Uppsala"
    fx_markup = float(0)
    fx_provider_markup = float(0)
    sales_markup = float(0)

    try:
        response_company = await pay_admin_client.create_company(
            company,
            address_lines,
            country_code,
            postal_code,
            city,
            fx_markup,
            fx_provider_markup,
            sales_markup,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_company err: %s", err.response.headers)
        logger.info("response_company body: %s", err.response.json())
        sys.exit(EXIT_MSG)

    logging.info("create_company: %s", json.dumps(response_company, indent=4))

    first_name = "J"
    last_name = "N"
    email_address = "jerzy.n{0}@snowfalltravel.com".format(return_randomized_token())
    phone_number = "+48123456789"

    try:
        response_create_contact = await pay_admin_client.create_contact(
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            phone_number=phone_number,
            company_id=response_company["data"]["id"],
        )
    except httpx.HTTPStatusError as err1:
        logger.info("response_create_contact err: %s", err1.response.headers)
        logger.info("response_create_contact body: %s", err1.response.json())
        sys.exit(EXIT_MSG)

    logger.info(
        "create_contacts: %s",
        json.dumps(response_create_contact, indent=4),
    )

    assert is_valid_uuid(response_create_contact["data"]["id"])
    assert response_create_contact["data"]["type"] == "contacts"
    assert response_create_contact["data"]["attributes"]["firstName"] == first_name
    assert response_create_contact["data"]["attributes"]["lastName"] == last_name
    assert (
        response_create_contact["data"]["attributes"]["emailAddress"] == email_address
    )
    assert response_create_contact["data"]["attributes"]["phoneNumber"] == phone_number
    company_data = response_create_contact["data"]["relationships"]["company"]["data"]
    assert is_valid_uuid(company_data["id"])
    assert company_data["id"] == response_company["data"]["id"]
    assert company_data["type"] == "companies"
