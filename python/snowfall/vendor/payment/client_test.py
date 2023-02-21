from snowfall.vendor.payment.client import PaymentClient
from snowfall.vendor.payment.errors import PaymentError
from snowfall.vendor.payment.models import contact


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


def test_permission_error_contact_write(
    payment_client_permission_issue: PaymentClient,
    contact_request: contact.ContactRequest,
) -> None:
    try:
        payment_client_permission_issue.create_contact(contact_request)
    except PaymentError as exc:
        assert (
            exc.message
            == "You do not have permission 'contact_write' to perform this operation"
        )
        assert exc.status == 400
