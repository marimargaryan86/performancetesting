from collections.abc import Callable, Sequence
from typing import Any

import pytest
from pytest_mock import MockerFixture

from snowfall.project.pay.adapter import transactions
from snowfall.project.pay.service.companies.v1.models_pb2 import (
    Account,
    Company,
)
from snowfall.stdlib import money


@pytest.fixture()
def available_currencies() -> Sequence[money.Currency]:
    return (
        money.Currency("USD"),
        money.Currency("GBP"),
        money.Currency("AMD"),
        money.Currency("SEK"),
    )


@pytest.fixture()
async def company(
    account: Account,
) -> Company:
    fx_markup = 1.2
    processing_markup = 2.2
    sales_markup = 2.3

    return Company(
        id=account.company_id,
        name="test_company",
        fx_markup=fx_markup,
        processing_markup=processing_markup,
        sales_markup=sales_markup,
        account_id=account.id,
    )


@pytest.fixture()
def transaction_ids() -> Sequence[str]:
    return [
        "e719b289-982c-42f0-99a2-63fa70f8f8c0",
        "c36649e6-71f1-4dfa-aa5a-01c0ede6e538",
    ]


@pytest.fixture()
async def booking_id(
    transaction_ids: Sequence[str],
    transactions_client: transactions.Client,
) -> str:
    return (await transactions_client.get(transaction_ids[0])).external_reference_id


class StripeCustomer(object):
    def __init__(self) -> None:
        self.id: str = "mock_stripe_customer_id"


class StripeEphemeralKey(object):
    def __init__(self) -> None:
        self.secret: str = "mocked_ephemeral_key_secret"


@pytest.fixture()
def stripe_customer(mocker: MockerFixture) -> StripeCustomer:
    return mocker.patch("stripe.Customer.create", return_value=StripeCustomer())


@pytest.fixture()
def stripe_ephemeral_key(mocker: MockerFixture) -> StripeEphemeralKey:
    return mocker.patch("stripe.EphemeralKey.create", return_value=StripeEphemeralKey())


@pytest.fixture()
def update_ory_identity(mocker: MockerFixture) -> str:
    return mocker.patch(
        "snowfall.adapter.identities.DictClient.update_ory_identity",
        return_value="yo",
    )


class StripePaymentIntent(object):
    def __init__(self) -> None:
        self.client_secret: str = "what_a_time_to_be_alive"
        self.stripe_id = "mock_stripe_id"


@pytest.fixture()
def create_payment_intent(mocker: MockerFixture) -> StripePaymentIntent:
    return mocker.patch(
        "stripe.PaymentIntent.create",
        return_value=StripePaymentIntent(),
    )


@pytest.fixture()
def mock_create_user_payload() -> Callable[[str, str, str], dict[str, Any]]:
    return _mock_create_user_payload


def _mock_create_user_payload(
    reseller_id: str | None = None,
    email: str = "example@test.com",
    role: str = "reseller-admin",
) -> dict[str, Any]:
    return {
        "type": "users",
        "attributes": {
            "email": email,
            "role": role,
        },
        "relationships": {
            "reseller": {
                "data": (
                    {
                        "id": reseller_id,
                        "type": "resellers",
                    }
                    if reseller_id
                    else None
                ),
            },
        },
    }
