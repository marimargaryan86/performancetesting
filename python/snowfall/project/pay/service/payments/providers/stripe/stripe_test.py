import pytest

from snowfall.project.pay.service.payments.providers.stripe.stripe import Stripe
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


@pytest.mark.usefixtures("_mock_stripe_customer")
async def test_create_and_get_credit_card_holder(
    stripe_client: Stripe,
    user_id: str,
) -> None:
    credit_card_holder = credit_card_models_pb2.CreditCardHolder(
        email="test@test.com",
        name="create_test",
    )
    (
        created_credit_card_holder,
        create_ephemeral_key,
    ) = await stripe_client.create_credit_card_holder(
        user_id,
        credit_card_holder,
    )

    (
        credit_card_holder,
        fetch_ephemeral_key,
    ) = await stripe_client.get_credit_card_holder(
        user_id,
    )
    assert credit_card_holder.id == created_credit_card_holder.id
    assert create_ephemeral_key != ""
    assert fetch_ephemeral_key != ""


@pytest.mark.usefixtures("_mock_stripe_payment_intent")
def test_create_and_get_credit_card_payment(
    stripe_client: Stripe,
    user_id: str,
) -> None:
    intent_money = money.from_string("100", money.Currency("USD"))
    payment_req = credit_card_models_pb2.CreditCardPayment(
        amount=intent_money.protobuf(),
        capture_method="manual",
        credit_card_holder_id="cus_PGQkLV2pMZKOxI",
        enable_automatic_payment_method=True,
    )
    created_payment = stripe_client.create_credit_card_payment(payment_req)

    fetched_payment = stripe_client.get_credit_card_payment(created_payment.id)

    assert fetched_payment is not None
    assert created_payment.id == fetched_payment.id
    assert created_payment.amount == fetched_payment.amount
