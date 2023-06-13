import json
import logging
from typing import Any, Mapping

import httpx
import pytest

from snowfall.project.junction.api_automation.conftest import (
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
from snowfall.vendor.currency_cloud.client import CurrencyCloudAuth, PaymentClient
from snowfall.vendor.junction.auth import UserAuth
from snowfall.vendor.junction.pay.client import Client as PayClient

logger = logging.getLogger()

PAY_TEST_ACCOUNT01 = "7e249624-535d-418a-8009-0908675136e1"
PAY_TEST_ACCOUNT02 = "026b616f-8e6b-42e4-abc7-559ef58a4d69"


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
        err_msg = json.dumps(err.response.json(), indent=4)  # noqa: WPS204
        pytest.fail(err_msg, pytrace=False)  # noqa: WPS204
    logger.info(
        "response_create_account: %s",
        json.dumps(response_create_account, indent=4),
    )
    return response_create_account


@pytest.fixture()
async def pay_create_beneficiary(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_create_beneficiary = await pay_admin_client.create_beneficiary(
            bank_account_holder_name="EUR test Account Holder",
            email="example@example.com",
            beneficiary_address_lines=[
                "Radhuset",
                "Våksalagatan 2",
                "United Spaces",
                "Sweden",
            ],
            beneficiary_country_code="DE",
            bank_name="mBank S.A.",
            account_type="checking",
            payment_types="priority",
            bank_address_lines=[
                "mBank S.A.",
                "Bankowość detaliczna",
                "Skrytka Pocztowa 2108",
                "90-959",
                "Łódź 2",
            ],
            bank_country_code="DE",
            currency_id="EUR",
            account_id=PAY_TEST_ACCOUNT01,
            beneficiary_postal_code="12345",
            beneficiary_city="Uppsala",
            bic_swift="BREXPLPWMBK",
            iban="DE89370400440532013000",
        )
    except httpx.HTTPStatusError as err:
        logger.info("response_create_beneficiary err: %s", err.response.headers)
        logger.info("response_create_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_beneficiary: %s",
        json.dumps(response_create_beneficiary, indent=4),
    )
    return response_create_beneficiary


@pytest.fixture()
async def pay_create_transaction_eur_sek(
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
    pay_create_quote_eur_sek: Mapping[str, Any],
) -> dict[str, Any]:
    external_reference = string.uuid()
    logger.info(": %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", pay_create_quote_eur_sek["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=pay_create_quote_eur_sek["data"]["id"],
        )

    except httpx.HTTPStatusError as err:
        logger.info("response err: %s", err.response.headers)
        logger.info("response_create_transactions body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    return response_create_transactions


@pytest.fixture()
async def pay_create_transaction_eur_usd(
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
    pay_create_quote_eur_usd: Mapping[str, Any],
) -> dict[str, Any]:
    external_reference = string.uuid()
    logger.info(": %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", pay_create_quote_eur_usd["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=pay_create_quote_eur_usd["data"]["id"],
        )

    except httpx.HTTPStatusError as err:
        logger.info("response err: %s", err.response.headers)
        logger.info("response_create_transactions body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "create_transactions: %s",
        json.dumps(response_create_transactions, indent=4),
    )

    return response_create_transactions


@pytest.fixture()
async def pay_create_transaction_sek_eur(
    pay_client: PayClient,
    pay_admin_client: PayAdminClient,
    pay_create_quote_sek_eur: Mapping[str, Any],
) -> dict[str, Any]:
    external_reference = string.uuid()
    logger.info(": %s", external_reference)
    invoice_reference = string.uuid()
    logger.info("invoice_reference: %s", invoice_reference)
    logger.info("quotation_id: %s", pay_create_quote_sek_eur["data"]["id"])

    try:
        response_create_transactions = await pay_client.create_transactions(
            external_reference=external_reference,
            invoice_reference=invoice_reference,
            quotation_id=pay_create_quote_sek_eur["data"]["id"],
        )

    except httpx.HTTPStatusError as err:
        logger.info("response err: %s", err.response.headers)
        logger.info("response_create_transactions body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

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
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
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
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
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
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
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
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("list_accounts: %s", json.dumps(response_list_accounts, indent=4))
    return response_list_accounts


@pytest.fixture()
async def pay_list_beneficiaries(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_list_beneficiaries = await pay_admin_client.list_beneficiaries()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_beneficiaries err: %s", err.response.headers)
        logger.info("response_list_beneficiaries body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("list_accounts: %s", json.dumps(response_list_beneficiaries, indent=4))
    return response_list_beneficiaries


@pytest.fixture()
async def pay_list_payments(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    try:
        response_list_payments = await pay_admin_client.list_payments()
    except httpx.HTTPStatusError as err:
        logger.info("response_list_payments err: %s", err.response.headers)
        logger.info("response_list_payments body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)

    logger.info(
        "list_payments: %s",
        json.dumps(
            response_list_payments,
            indent=4,
        ),
    )
    return response_list_payments


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


@pytest.fixture()
def payment_test_client(
    api_token: str,
    host: str,
) -> PaymentClient:
    login = get_variable_value(host, api_token, "pay_api_cc_login")
    api_key = get_variable_value(host, api_token, "pay_api_cc_api_key")

    base_url = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_api_cc_address"),
    )

    return PaymentClient(
        base_url=base_url,
        auth=CurrencyCloudAuth(base_url, login, api_key),
    )


async def create_company(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    float0 = float(0)
    try:
        response_company = await pay_admin_client.create_company(
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
        logger.info("response_company err: %s", err.response.headers)
        logger.info("response_company body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("create_company: %s", json.dumps(response_company, indent=4))
    return response_company


expected_currencies_list = [
    "AUD",
    "BHD",
    "BGN",
    "CAD",
    "CNY",
    "CZK",
    "DKK",
    "EUR",
    "HKD",
    "HUF",
    "ILS",
    "JPY",
    "KES",
    "KWD",
    "NZD",
    "NOK",
    "OMR",
    "PLN",
    "QAR",
    "RON",
    "SAR",
    "SGD",
    "ZAR",
    "SEK",
    "CHF",
    "THB",
    "TRY",
    "UGX",
    "GBP",
    "AED",
    "USD",
]


@pytest.fixture()
def pay_admin_client(
    api_token: str,
    host: str,
) -> PayAdminClient:
    email = get_variable_value(host, api_token, "pay_api_test_email")
    password = get_variable_value(host, api_token, "pay_api_test_password")

    base_url_admin_api = "{0}{1}".format(
        HTTPS_PREFIX,
        get_variable_value(host, api_token, "pay_admin_api_host"),
    )

    auth = UserAuth(
        base_url=base_url_admin_api,
        email=email,
        password=password,
    )

    return PayAdminClient(
        base_url=base_url_admin_api,
        auth=auth,
    )


@pytest.fixture()
async def pay_create_company_beneficiary(
    pay_admin_client: PayAdminClient,
) -> dict[str, Any]:
    float0 = float(0)
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
    except httpx.HTTPStatusError as err:
        logger.info("response_beneficiary err: %s", err.response.headers)
        logger.info("response_beneficiary body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    return response_beneficiary


@pytest.fixture()
async def pay_create_company_payer(
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
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    return response_payer


@pytest.fixture()
async def pay_create_quote_eur_sek(
    pay_client: PayClient,
    pay_create_company_payer: Mapping[str, Any],
    pay_create_company_beneficiary: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=pay_create_company_payer["data"]["id"],
            beneficiary_id=pay_create_company_beneficiary["data"]["id"],
            from_currency="EUR",
            to_currency="SEK",
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_quote err: %s",
            err.response.headers,
        )
        logger.info("response_create_quote body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))
    return response_create_quote


@pytest.fixture()
async def pay_create_quote_eur_usd(
    pay_client: PayClient,
    pay_create_company_payer: Mapping[str, Any],
    pay_create_company_beneficiary: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=pay_create_company_payer["data"]["id"],
            beneficiary_id=pay_create_company_beneficiary["data"]["id"],
            from_currency="EUR",
            to_currency="USD",
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_quote err: %s",
            err.response.headers,
        )
        logger.info("response_create_quote body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))
    return response_create_quote


@pytest.fixture()
async def pay_create_quote_sek_eur(
    pay_client: PayClient,
    pay_create_company_payer: Mapping[str, Any],
    pay_create_company_beneficiary: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        response_create_quote = await pay_client.create_quote(
            amount=1000,
            external_reference=string.uuid(),
            payer_id=pay_create_company_payer["data"]["id"],
            beneficiary_id=pay_create_company_beneficiary["data"]["id"],
            from_currency="SEK",
            to_currency="EUR",
        )
    except httpx.HTTPStatusError as err:
        logger.info(
            "response_create_quote err: %s",
            err.response.headers,
        )
        logger.info("response_create_quote body: %s", err.response.json())
        err_msg = json.dumps(err.response.json(), indent=4)
        pytest.fail(err_msg, pytrace=False)
    logger.info("create_quote: %s", json.dumps(response_create_quote, indent=4))
    return response_create_quote
