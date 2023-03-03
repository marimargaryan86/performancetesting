import json
import logging
import sys

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.vendor.pay.client import PayAdminClient

logger = logging.getLogger()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
)
se = logging.StreamHandler(sys.stderr)
se.setFormatter(formatter)
logger.addHandler(se)
logger.setLevel(logging.DEBUG)


@pytest.mark.integration
async def test_create_company(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    company = "test-company-{0}".format(return_randomized_token())
    address_lines = ["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"]
    country_code = "SE"
    postal_code = "75320"
    city = "Uppsala"
    buffer_rate = float(0)
    sales_rate = float(0)

    response = await pay_admin_client.create_company(
        company,
        address_lines,
        country_code,
        postal_code,
        city,
        buffer_rate,
        sales_rate,
    )

    logging.info("create_company: %s", json.dumps(response, indent=4))

    assert (
        is_valid_uuid(response["data"]["id"]) is True
    ), "company uuid must be in valid format"
    assert response["data"]["type"] == "companies"
    assert response["data"]["attributes"]["name"] == company
    assert response["data"]["attributes"]["address"]["addressLines"] == address_lines
    assert response["data"]["attributes"]["address"]["countryCode"] == country_code
    assert response["data"]["attributes"]["address"]["postalCode"] == postal_code
    assert response["data"]["attributes"]["address"]["city"] == city
    assert response["data"]["attributes"]["bufferRate"] == buffer_rate
    assert response["data"]["attributes"]["salesRate"] == sales_rate
