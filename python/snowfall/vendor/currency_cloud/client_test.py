import pytest

from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.errors import CurrencyCloudError
from snowfall.vendor.currency_cloud.models import account, contact


def test_contact_pass_case(
    payment_client_pass_case: PaymentClient,
    contact_request: contact.ContactRequest,
    contact_response: contact.ContactResponse,
) -> None:
    contact_response_res = payment_client_pass_case.create_contact(contact_request)
    assert contact_response_res.identifier == contact_response.identifier
    assert contact_response_res.first_name == contact_response.first_name
    assert contact_response_res.last_name == contact_response.last_name
    assert contact_response_res.phone_number == contact_response.phone_number
    assert contact_response_res.email_address == contact_response.email_address


def test_account_pass_case(  # noqa: WPS218
    payment_client_pass_case: PaymentClient,
    account_request: account.AccountRequest,
    account_response: account.AccountResponse,
) -> None:
    account_response_res = payment_client_pass_case.create_account(
        account_request,
    )
    assert account_response_res.identifier == account_response.identifier
    assert account_response_res.account_name == account_response.account_name
    assert account_response_res.legal_entity_type == account_response.legal_entity_type
    assert account_response_res.street == account_response.street
    assert account_response_res.city == account_response.city
    assert account_response_res.state_or_province == account_response.state_or_province
    assert account_response_res.country == account_response.country
    assert account_response_res.postal_code == account_response.postal_code
    assert account_response_res.spread_table == account_response.spread_table
    assert account_response_res.api_trading == account_response.api_trading
    assert account_response_res.online_trading == account_response.online_trading
    assert account_response_res.phone_trading == account_response.phone_trading
    assert (
        account_response_res.terms_and_conditions_accepted
        == account_response.terms_and_conditions_accepted
    )


def test_permission_error_contact_write(
    payment_client_permission_contact_issue: PaymentClient,
    contact_request: contact.ContactRequest,
) -> None:
    with pytest.raises(
        CurrencyCloudError,
        match="You do not have permission 'contact_write' to perform this operation",
    ):
        payment_client_permission_contact_issue.create_contact(contact_request)


def test_permission_error_account_write(
    payment_client_permission_account_issue: PaymentClient,
    account_request: account.AccountRequest,
) -> None:
    with pytest.raises(
        CurrencyCloudError,
        match="You do not have permission 'account_write' to perform this operation",
    ):
        payment_client_permission_account_issue.create_account(account_request)
