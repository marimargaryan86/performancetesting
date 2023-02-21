from unittest import mock

import currencycloud
import pytest

from snowfall.stdlib import string
from snowfall.vendor.payment.client import PaymentClient
from snowfall.vendor.payment.models import contact


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
def payment_client_pass_case(
    contact_response: contact.ContactResponse,
) -> PaymentClient:
    resource = mock.Mock()
    resource._attributes = contact_response.dict(by_alias=True)  # noqa: WPS437

    cc_client = mock.Mock()
    cc_client.contacts = mock.Mock()
    cc_client.contacts.create = mock.Mock(
        return_value=resource,
    )
    return PaymentClient(cc_client)


@pytest.fixture()
def payment_client_permission_issue() -> currencycloud.Client:
    json_data = {
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
    response = mock.Mock()
    response.status_code = 403
    response.json = mock.Mock(return_value=json_data)

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
    return PaymentClient(cc_client)
