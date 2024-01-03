from unittest import mock

import mongomock_motor
import pytest
import stripe

from snowfall.project.pay.service.payments.providers.stripe.repositories import (
    PaymentUsersRepository,
)
from snowfall.project.pay.service.payments.providers.stripe.stripe import Stripe
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout

_logger = stdout.get_logger()


@pytest.fixture()
def mongo_client() -> mongomock_motor.AsyncMongoMockClient:
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture()
def stripe_test_key() -> str:
    return "stripe_test_key"


@pytest.fixture()
def user_id() -> str:
    return "test_user_id"


@pytest.fixture()
def stripe_user() -> credit_card_models_pb2.PaymentUser:
    return credit_card_models_pb2.PaymentUser(
        id=string.uuid(),
        internal_user_id=string.uuid(),
    )


@pytest.fixture()
async def stripe_client(
    mongo_client: mongomock_motor.AsyncMongoMockClient,
    stripe_user: credit_card_models_pb2.PaymentUser,
    stripe_test_key: str,
) -> Stripe:
    repo = PaymentUsersRepository(
        collection=mongo_client.test.stripe_users,
    )
    await repo.insert(stripe_user)

    stripe_version = "2020-08-27"

    return Stripe(
        repo,
        stripe_version,
        stripe_test_key,
    )


@pytest.fixture()
def _mock_stripe_customer() -> None:
    create_customer = mock.Mock(
        id="44ad8b84-c1d7-45d9-95bb-db725b6340cf",
    )
    get_customer = mock.Mock(
        id="44ad8b84-c1d7-45d9-95bb-db725b6340cf",
        email="test@test.com",
    )
    get_customer.name = "test"

    stripe.Customer.create = mock.Mock(return_value=create_customer)  # type: ignore[method-assign]
    stripe.Customer.retrieve = mock.Mock(return_value=get_customer)  # type: ignore[method-assign]

    ephemeral_secret = mock.Mock()
    ephemeral_secret.secret = "ephemeral_secret"
    stripe.EphemeralKey.create = ephemeral_secret  # type: ignore[method-assign]


@pytest.fixture()
def _mock_stripe_payment_intent() -> None:
    create_payment = mock.Mock(
        id="bcad52bc-fe35-4717-840a-b047d59baa9d",
        client_secret="client_secret",
    )
    get_payment = mock.Mock(
        id="bcad52bc-fe35-4717-840a-b047d59baa9d",
        amount=10000,
        currency="usd",
        capture_method="manual",
        customer="cus_PGQkLV2pMZKOxI",
        automatic_payment_methods={"enabled": True},
        client_secret="client_secret",
    )
    stripe.PaymentIntent.create = mock.Mock(return_value=create_payment)  # type: ignore[method-assign]
    stripe.PaymentIntent.retrieve = mock.Mock(return_value=get_payment)  # type: ignore[method-assign]
