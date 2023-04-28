import datetime
from typing import Any, Mapping
from unittest import mock

import currencycloud
import pytest

from snowfall.stdlib import string
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models import account, contact


@pytest.fixture()
def contact_request() -> contact.ContactRequest:
    return contact.ContactRequest(
        account_id=string.uuid(),
        first_name="Test or Test",
        last_name="Test",
        phone_number="123456789",
        email_address="test@test.com",
    )


@pytest.fixture()
def contact_response() -> contact.ContactResponse:
    return contact.ContactResponse(
        identifier=string.uuid(),
        first_name="Test or Test",
        last_name="Test",
        phone_number="123456789",
        email_address="test@test.com",
    )


@pytest.fixture()
def account_request() -> account.AccountRequest:
    return account.AccountRequest(
        account_name="Company",
        legal_entity_type="company",
        street="new street 12",
        city="London",
        state_or_province="London",
        country="UK",
        postal_code="4325",
    )


@pytest.fixture()
def account_response() -> account.AccountResponse:
    return account.AccountResponse(
        identifier=string.uuid(),
        account_name="Company",
        legal_entity_type="company",
        street="new street 12",
        city="London",
        state_or_province="London",
        country="UK",
        status="enabled",
        postal_code="4325",
        spread_table="flat_0.00",
        api_trading=True,
        online_trading=False,
        phone_trading=True,
        terms_and_conditions_accepted=True,
        updated_at=datetime.datetime.now(tz=datetime.timezone.utc),
    )


@pytest.fixture()
def payment_client_pass_case(
    contact_response: contact.ContactResponse,
    account_response: account.AccountResponse,
) -> PaymentClient:
    resource = mock.Mock()
    resource._attributes = contact_response.dict(by_alias=True)  # noqa: WPS437

    cc_client = mock.Mock()
    cc_client.contacts = mock.Mock()
    cc_client.contacts.create = mock.Mock(
        return_value=resource,
    )

    resource_account = mock.Mock()
    resource_account._attributes = account_response.dict(  # noqa: WPS437
        by_alias=True,
    )
    cc_client.accounts = mock.Mock()
    cc_client.accounts.create = mock.Mock(
        return_value=resource_account,
    )
    config = mock.Mock()
    config.client = cc_client
    return PaymentClient(config)


@pytest.fixture()
def permission_issue_contact_write_error() -> Mapping[str, Any]:
    return {
        "error_code": "permission_denied",
        "error_messages": {
            "base": [
                {
                    "code": "permission_denied",
                    "message": "You do not have permission 'contact_write'{0}".format(
                        " to perform this operation",
                    ),
                    "params": {},
                },
            ],
        },
    }


@pytest.fixture()
def permission_issue_account_write_error() -> Mapping[str, Any]:
    return {
        "error_code": "permission_denied",
        "error_messages": {
            "base": [
                {
                    "code": "permission_denied",
                    "message": "You do not have permission 'account_write'{0}".format(
                        " to perform this operation",
                    ),
                    "params": {},
                },
            ],
        },
    }


@pytest.fixture()
def payment_client_permission_contact_issue(
    permission_issue_contact_write_error: Mapping[str, Any],
) -> PaymentClient:
    response = mock.Mock()
    response.status_code = 403
    response.json = mock.Mock(return_value=permission_issue_contact_write_error)

    cc_client = mock.Mock()
    cc_client.contacts = mock.Mock()
    cc_client.contacts.create = mock.Mock(
        side_effect=currencycloud.errors.api.ForbiddenError(
            "post",
            "endpoint/",
            {},
            response,
        ),
    )
    config = mock.Mock()
    config.client = cc_client
    return PaymentClient(config)


@pytest.fixture()
def payment_client_permission_account_issue(
    permission_issue_account_write_error: Mapping[str, Any],
) -> PaymentClient:
    response = mock.Mock()
    response.status_code = 403
    response.json = mock.Mock(return_value=permission_issue_account_write_error)

    cc_client = mock.Mock()
    cc_client.accounts = mock.Mock()
    cc_client.accounts.create = mock.Mock(
        side_effect=currencycloud.errors.api.ForbiddenError(
            "post",
            "endpoint/",
            {},
            response,
        ),
    )
    config = mock.Mock()
    config.client = cc_client
    return PaymentClient(config)
