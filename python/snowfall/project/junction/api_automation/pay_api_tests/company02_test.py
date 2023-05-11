import json
import logging

import pytest

from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_update_company(  # noqa: WPS210, WPS218
    pay_admin_client: PayAdminClient,
) -> None:
    company = "test-company-{0}".format(return_randomized_token())
    address_lines = ["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"]
    country_code = "SE"
    postal_code = "75320"
    city = "Uppsala"
    fx_markup = float(0)
    processing_markup = float(0)
    sales_markup = float(0)

    response_create = await pay_admin_client.create_company(
        company,
        address_lines,
        country_code,
        postal_code,
        city,
        fx_markup,
        processing_markup,
        sales_markup,
    )

    logging.info("create_company: %s", json.dumps(response_create, indent=4))

    update_company = company
    update_address_lines = [
        "updated_Radhuset",
        "updated_Våksalagatan 2",
        "updated_United Spaces",
        "updated_Sweden",
    ]
    update_country_code = "PL"
    update_postal_code = "updated_75320"
    update_city = "updated_Uppsala"
    updated_fx_markup = float(1)
    updated_processing_markup = float(1)
    updated_sales_markup = float(1)

    response = await pay_admin_client.update_company(
        response_create["data"]["id"],
        update_company,
        update_address_lines,
        update_country_code,
        update_postal_code,
        update_city,
        updated_fx_markup,
        updated_processing_markup,
        updated_sales_markup,
    )

    logging.info("update_company: %s", json.dumps(response, indent=4))

    assert is_valid_uuid(response["data"]["id"]), "company uuid must be in valid format"
    assert response["data"]["id"] == response_create["data"]["id"]
    assert response["data"]["type"] == "companies"
    assert response["data"]["attributes"]["name"] == update_company
    assert (
        response["data"]["attributes"]["address"]["addressLines"]
        == update_address_lines
    )
    assert (
        response["data"]["attributes"]["address"]["countryCode"] == update_country_code
    )
    assert response["data"]["attributes"]["address"]["postalCode"] == update_postal_code
    assert response["data"]["attributes"]["address"]["city"] == update_city
    assert response["data"]["attributes"]["fxMarkup"] == updated_fx_markup
    assert (
        response["data"]["attributes"]["processingMarkup"] == updated_processing_markup
    )
    assert response["data"]["attributes"]["salesMarkup"] == updated_sales_markup
