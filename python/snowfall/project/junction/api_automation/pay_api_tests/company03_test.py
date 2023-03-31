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
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration()
async def test_get_company(  # noqa: WPS210, WPS218
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
        response_create = await pay_admin_client.create_company(
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

    logging.info("create_company: %s", json.dumps(response_create, indent=4))

    response = await pay_admin_client.get_company_details(
        response_create["data"]["id"],
    )
    logger.info("get_company_details: %s", json.dumps(response, indent=4))

    assert is_valid_uuid(response["data"]["id"]), "company uuid must be in valid format"
    assert response["data"]["id"] == response_create["data"]["id"]
    assert response["data"]["type"] == "companies"
    assert response["data"]["attributes"]["name"] == company
    assert response["data"]["attributes"]["address"]["addressLines"] == address_lines
    assert response["data"]["attributes"]["address"]["countryCode"] == country_code
    assert response["data"]["attributes"]["address"]["postalCode"] == postal_code
    assert response["data"]["attributes"]["address"]["city"] == city
    assert response["data"]["attributes"]["fxMarkup"] == fx_markup
    assert response["data"]["attributes"]["fxProviderMarkup"] == fx_provider_markup
    assert response["data"]["attributes"]["salesMarkup"] == sales_markup
