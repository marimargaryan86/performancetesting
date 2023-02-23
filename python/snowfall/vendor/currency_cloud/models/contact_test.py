from snowfall.vendor.currency_cloud.models import contact


def test_exclude_characters() -> None:
    expected = "TestTest"
    contact_request = contact.ContactRequest(
        account_id="1234",
        first_name="<<Test>><<><Test",
        last_name="<<Test>><<><Test",
        email_address="test@test.com",
        phone_number="+123456789",
    )
    contact.exclude_characters(contact_request)
    assert contact_request.first_name == expected
    assert contact_request.last_name == expected
