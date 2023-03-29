import logging
from typing import Any, Mapping, Sequence

import pytest

from snowfall.project.junction.api_automation.conftest import create_company
from snowfall.project.junction.api_automation.test_functions.helpers_api import (
    is_valid_uuid,
)
from snowfall.stdlib.format import jsonapi
from snowfall.vendor.pay.client import PayAdminClient, get_all_resources

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
EXIT_MSG = "Exiting ; check your logs"


@pytest.mark.integration
async def test_list_companies(
    pay_admin_client: PayAdminClient,
) -> None:
    all_companies_before_create_new_one = await get_all_resources(
        pay_admin_client.list_companies,
        limit=100,
        cursor="",
        logger=logger,
    )

    all_accountless_companies_before_create_new_one = await get_all_resources(
        pay_admin_client.list_accountless_companies,
        limit=100,
        cursor="",
        logger=logger,
    )
    logger.info(
        "Companies number before create new one: %i",
        len(all_companies_before_create_new_one),
    )
    logger.info(
        "Accountless Companies number before create new one: %i",
        len(all_accountless_companies_before_create_new_one),
    )

    company_payload = await create_company(pay_admin_client)

    all_companies = await get_all_resources(
        pay_admin_client.list_companies,
        limit=100,
        cursor="",
        logger=logger,
    )

    all_accountless_companies = await get_all_resources(
        pay_admin_client.list_accountless_companies,
        limit=100,
        cursor="",
        logger=logger,
    )

    logger.info("Companies number: %i", len(all_companies))
    logger.info(
        "Accountless Companies number: %i",
        len(all_accountless_companies),
    )

    _check_new_company_existence_in_all_companies(
        all_companies,
        all_companies_before_create_new_one,
        company_payload,
    )
    _check_new_company_existence_in_all_companies(
        all_accountless_companies,
        all_accountless_companies_before_create_new_one,
        company_payload,
    )


def _check_new_company_existence_in_all_companies(  # noqa: WPS218
    all_companies: Sequence[Mapping[str, Any]],
    all_companies_before_create_new_one: Sequence[Mapping[str, Any]],
    new_company_payload: Mapping[str, Any],
) -> None:
    flatten_payload = jsonapi.flatten_resource(new_company_payload["data"])
    assert len(all_companies) == len(all_companies_before_create_new_one) + 1
    for company in all_companies:
        if company["id"] == new_company_payload["data"]["id"]:
            flat_company = jsonapi.flatten_resource(company)
            assert is_valid_uuid(company["id"]), "company uuid must be in valid format"
            assert company["id"] == new_company_payload["data"]["id"]
            assert company["type"] == new_company_payload["data"]["type"]
            assert flat_company["name"] == flatten_payload["name"]
            assert (
                flat_company["address"]["addressLines"]
                == flatten_payload["address"]["addressLines"]
            )
            assert (
                flat_company["address"]["countryCode"]
                == flatten_payload["address"]["countryCode"]
            )
            assert (
                flat_company["address"]["postalCode"]
                == flatten_payload["address"]["postalCode"]
            )
            assert flat_company["address"]["city"] == flatten_payload["address"]["city"]
            assert flat_company["fxMarkup"] == flatten_payload["fxMarkup"]
            assert (
                flat_company["fxProviderMarkup"] == flatten_payload["fxProviderMarkup"]
            )
            assert flat_company["salesMarkup"] == flatten_payload["salesMarkup"]
            break
    else:
        raise AssertionError("New created company is not found in all companies")
