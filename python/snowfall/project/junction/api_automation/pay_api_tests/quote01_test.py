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
from snowfall.stdlib import string
from snowfall.vendor.junction.pay.client import Client

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@pytest.mark.integration()
async def test_create_quote(  # noqa: WPS218
    pay_admin_client: PayAdminClient,
    pay_client: Client,
) -> None:
    response_payer = await pay_admin_client.create_company(
        company="test-company-{0}".format(return_randomized_token()),
        address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
        country_code="SE",
        postal_code="75320",
        city="Uppsala",
        fx_markup=float(0),
        fx_provider_markup=float(0),
        sales_markup=float(0),
    )

    response_beneficiary = await pay_admin_client.create_company(
        company="test-company-{0}".format(return_randomized_token()),
        address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
        country_code="SE",
        postal_code="75320",
        city="Uppsala",
        fx_markup=float(0),
        fx_provider_markup=float(0),
        sales_markup=float(0),
    )

    response_create_quote = await pay_client.create_quote(
        amount=1000,
        external_reference=string.uuid(),
        payer_id=response_payer["data"]["id"],
        beneficiary_id=response_beneficiary["data"]["id"],
        from_currency="USD",
        to_currency="EUR",
    )
    logging.info("quote: %s", json.dumps(response_create_quote, indent=4))

    relationships = response_create_quote["data"]["relationships"]

    assert (
        is_valid_uuid(response_create_quote["data"]["id"]) is True
    ), "quotes uuid must be in valid format"
    assert response_create_quote["data"]["type"] == "quotes"
    assert isinstance(response_create_quote["data"]["attributes"]["amount"], int)
    assert relationships["fromCurrency"]["data"]["id"] == "USD"
    assert relationships["toCurrency"]["data"]["id"] == "EUR"
    assert relationships["payer"]["data"]["id"] == response_payer["data"]["id"]
    assert (
        relationships["beneficiary"]["data"]["id"] == response_beneficiary["data"]["id"]
    )
