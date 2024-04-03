from collections.abc import AsyncIterator, Mapping, Sequence
from unittest import mock

import httpx
import pytest
from starlette import applications
from starlette.middleware import Middleware

from snowfall.project.junction.go import fixtures as go_fixtures
from snowfall.project.junction.go.adapter import orders
from snowfall.project.pay import fixtures as pay_fixtures
from snowfall.project.pay.adapter import refunds, transactions
from snowfall.project.pay.service.refunds.v1.models_pb2 import Refund
from snowfall.project.pay.service.transactions.v1.models_pb2 import (
    Transaction,
)
from snowfall.project.pay.service.webhooks import bootstrap, routers
from snowfall.project.pay.service.webhooks.middlewares import (
    SignatureVerificationMiddleware,
)
from snowfall.project.pay.service.webhooks.states.stripe.invoice import InvoiceState
from snowfall.project.pay.service.webhooks.states.stripe.refunds import RefundsState
from snowfall.stdlib import string
from snowfall.stdlib.integration.starlette import application


@pytest.fixture()
def stripe_secret_key_for_refund() -> str:
    return "Very-Secret-Key"


@pytest.fixture()
def stripe_secret_key_for_invoice() -> str:
    return "Very-Secret-Key"


@pytest.fixture()
def refund_models() -> Sequence[Refund]:
    return [
        pay_fixtures.generate_refund(refund_id)
        for refund_id in (string.uuid(), string.uuid())
    ]


@pytest.fixture()
def transaction_models() -> Sequence[Transaction]:
    return [
        pay_fixtures.generate_transaction(transaction_id)
        for transaction_id in (string.uuid(), string.uuid())
    ]


@pytest.fixture()
def refunds_client(
    refund_models: Sequence[Refund],
    transaction_models: Sequence[Transaction],
    cc_payment_client: mock.Mock,
) -> refunds.DictClient:
    return refunds.DictClient(
        refund_models,
        transaction_models,
        cc_payment_client,
    )


@pytest.fixture()
def transactions_client(
    transaction_models: Sequence[Transaction],
) -> transactions.Client:
    return transactions.DictClient(transaction_models)


@pytest.fixture()
def orders_client() -> orders.Client:
    return orders.DictClient(
        go_fixtures.get_journeys(),
        go_fixtures.get_cancellation_requests(),
    )


@pytest.fixture()
def stripe_api_key() -> str:
    return "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


@pytest.fixture()
def refund_state(
    stripe_api_key: str,
    refunds_client: refunds.Client,
    transactions_client: transactions.Client,
    orders_client: orders.Client,
) -> RefundsState:
    return RefundsState(
        stripe_api_key,
        refunds_client,
        transactions_client,
        orders_client,
    )


@pytest.fixture()
def invoice_state(
    stripe_api_key: str,
    transactions_client: transactions.Client,
) -> InvoiceState:
    return InvoiceState(
        stripe_api_key,
        transactions_client,
    )


@pytest.fixture()
def headers() -> dict[str, str]:
    return {}


@pytest.fixture()
def webhook_app(
    refund_state: RefundsState,
    invoice_sate: InvoiceState,
    stripe_secret_key_for_refund: str,
    stripe_secret_key_for_invoice: str,
) -> applications.Starlette:
    return create_webhook_app(
        refund_state=refund_state,
        invoice_sate=invoice_sate,
        stripe_secret_key_for_refund=stripe_secret_key_for_refund,
        stripe_secret_key_for_invoice=stripe_secret_key_for_invoice,
    )


def create_webhook_app(
    refund_state: RefundsState,
    invoice_sate: InvoiceState,
    stripe_secret_key_for_refund: str,
    stripe_secret_key_for_invoice: str,
) -> applications.Starlette:
    return application.create_starlette_app(
        custom_middlewares=[
            Middleware(
                SignatureVerificationMiddleware,
                stripe_secret_key_for_refund=stripe_secret_key_for_refund,
                stripe_secret_key_for_invoice=stripe_secret_key_for_invoice,
            ),
        ],
        routes=routers.get_routes(
            bootstrap.create_dependencies(
                refunds_state=refund_state,
                invoice_state=invoice_sate,
            ),
        ),
        openapi_path=None,
    )


@pytest.fixture()
async def webhook_client(
    webhook_app: applications.Starlette,
    headers: Mapping[str, str],
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        app=webhook_app,
        base_url="https://example.com",
    ) as client:
        client.headers.update(headers)

        yield client
