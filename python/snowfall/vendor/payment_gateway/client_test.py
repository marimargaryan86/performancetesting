import pytest

from snowfall.vendor.payment_gateway.client import PayGwClient
from snowfall.vendor.payment_gateway.models.credit_card import (
    BillingAddress,
    CreditCardAttributes,
)
from snowfall.vendor.payment_gateway.models.transaction_token import (
    TransactionTokenAttributes,
)


@pytest.mark.integration()
async def test_credit_card_add_flow(
    pay_gw_client: PayGwClient,
    j1_session: str,
    j1_user: int,
) -> None:
    transaction_token = await pay_gw_client.transaction_token(
        TransactionTokenAttributes(user_id=j1_user, session_token=j1_session),
    )

    await pay_gw_client.credit_card(
        CreditCardAttributes(
            number="4242424242424242",
            cvc="443",
            expiration="11/2025",
            holder_name="Sargis Aghabekyan",
            is_default=True,
            billing_address=BillingAddress(
                country="US",
                country_code="US",
                state="AL",
                state_code="AL",
                city="Test",
                address1="123 Main Street",
                zip_code="22222",
            ),
        ),
        transaction_token,
    )
