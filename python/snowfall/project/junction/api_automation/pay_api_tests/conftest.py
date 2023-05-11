import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import (
    EXIT_MSG,
    HTTPS_PREFIX,
    get_variable_value,
)
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    return_randomized_token,
)
from snowfall.project.junction.api_automation.test_functions.pay_admin_client import (
    PayAdminClient,
)
from snowfall.stdlib import string
from snowfall.vendor.junction.auth import UserAuth
from snowfall.vendor.junction.pay.client import Client as PayClient

logger = logging.getLogger()

PAY_TEST_ACCOUNT01 = "009822ce-70fe-4f6d-b2d6-1f807f9cc5c4"
PAY_TEST_ACCOUNT02 = "00a986b5-5609-418c-bd63-e8f927fac6da"


@pytest.fixture()
async def pay_create_account(
    pay_admin_client: PayAdminClient,
    pay_create_contact: Mapping[str, Any],
) -> dict[str, Any]:
    name = "test account {0}".format(return_randomized_token())
    try:
        response_create_account = await pay_admin_client.create_accounts(
            name,
            pay_create_contact["data"]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_account: %s", err.response.headers)
        logger.info("response_create_account body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)  # noqa: WPS204
    logger.info(
        "response_create_account: %s",
        json.dumps(response_create_account, indent=4),
    )
    return response_create_account


@pytest.fixture()
async def pay_create_transaction(  # noqa: WPS210, WPS213, C901
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    float0 = float(0)
    try:
        response_payer = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float0,
            processing_markup=float0,
            sales_markup=float0,
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_payer err: %s", err.response.headers)
        logger.info("response_payer body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    try:
        response_beneficiary = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float0,
            processing_markup=float0,
            sales_markup=float0,
        )
    except httpx.HTTPStatusError as err1:
        logger.info("response_beneficiary err:: %s", err1.response.headers)
        logger.info("response_beneficiary body: %s", err1.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=response_payer["data"]["id"],
            beneficiary_id=response_beneficiary["data"]["id"],
            from_currency="EUR",
            to_currency="SEK",
        )
    except httpx.HTTPStatusError as err2:
        logger.info(
            "response_create_quote err: %s",
            err2.response.headers,
        )
        logger.info("response_create_quote body: %s", err2.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))

    external_reference = string.uuid()
    logger.info(": %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", response_create_quote["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=response_create_quote["data"]["id"],
        )

    except httpx.HTTPStatusError as err3:
        logger.info("response err:: %s", err3.response.headers)
        logger.info("response_create_transactions body: %s", err3.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    return response_create_transactions


@pytest.fixture()
async def pay_create_company(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    return await create_company(pay_admin_client)


@pytest.fixture()
async def pay_create_contact(
    pay_admin_client: PayAdminClient,
    pay_create_company: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        response_create_contact = await pay_admin_client.create_contact(
            first_name="J",
            last_name="N",
            email_address="jerzy.n{0}@snowfalltravel.com".format(
                return_randomized_token(),
            ),
            phone_number="+48123456789",
            company_id=pay_create_company["data"]["id"],
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_contact err: %s", err.response.headers)
        logger.info("response_create_contact body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info(
        "create_contacts: %s",
        json.dumps(response_create_contact, indent=4),
    )
    return response_create_contact


@pytest.fixture()
async def pay_list_all_currencies(
    pay_client: PayClient,
) -> dict[str, Any]:
    try:
        response_list_all_currencies = await pay_client.list_all_currencies()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_all_currencies err: %s", err.response.headers)
        logger.info("response_list_all_currencies body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info(
        "list_all_currencies: %s",
        json.dumps(response_list_all_currencies, indent=4),
    )
    return response_list_all_currencies


@pytest.fixture()
async def pay_get_accounts(
    pay_admin_client: PayAdminClient,
    pay_create_account: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        response_get_accounts = await pay_admin_client.get_accounts()
    except httpx.HTTPStatusError as err:
        logger.info("response_get_accounts err: %s", err.response.headers)
        logger.info("response_get_accounts body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)
    logger.info("get_accounts: %s", json.dumps(response_get_accounts, indent=4))
    return response_get_accounts


@pytest.fixture()
async def pay_list_accounts(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_list_accounts = await pay_admin_client.get_accounts()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_accounts err: %s", err.response.headers)
        logger.info("response_list_accounts body: %s", err.response.json())
        pytest.fail(err.response.json(), pytrace=False)
    logger.info("list_accounts: %s", json.dumps(response_list_accounts, indent=4))
    return response_list_accounts


@pytest.fixture()
def pay_client(
    api_token: str,
    host: str,
) -> PayClient:
    email = get_variable_value(host, api_token, "pay_api_test_email")
    password = get_variable_value(host, api_token, "pay_api_test_password")
    base_url_admin_api = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_admin_api_host"),
    )
    base_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_api_host"),
    )

    auth = UserAuth(
        base_url=base_url_admin_api,
        email=email,
        password=password,
    )

    return PayClient(
        base_url=base_url,
        auth=auth,
    )


async def create_company(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_company = await pay_admin_client.create_company(
            company="test-company-{0}".format(return_randomized_token()),
            address_lines=["Radhuset", "Våksalagatan 2", "United Spaces", "Sweden"],
            country_code="SE",
            postal_code="75320",
            city="Uppsala",
            fx_markup=float(0),
            processing_markup=float(0),
            sales_markup=float(0),
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_company err: %s", err.response.headers)
        logger.info("response_company body: %s", err.response.json())
        pytest.fail(EXIT_MSG, pytrace=False)
    logger.info("create_company: %s", json.dumps(response_company, indent=4))
    return response_company
