import logging

import pytest

from snowfall.project.junction.api_automation.conftest import get_variable_value
from snowfall.project.pay.service.payments.v1alpha import payments_pb2_grpc
from snowfall.stdlib.transport.grpc.client import create_channel

logger = logging.getLogger()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--GRPC-PAYMENT-SERVICE-HOST",
        help="grpc payment service host to perform calls",
    )


@pytest.fixture(scope="module")
def grpc_payment_service_stub(
    request: pytest.FixtureRequest,
) -> payments_pb2_grpc.PaymentsServiceStub:
    return payments_pb2_grpc.PaymentsServiceStub(
        create_channel(request.config.getoption("GRPC_PAYMENT_SERVICE_HOST")),
    )


@pytest.fixture()
def pay_webhook_secret_key(
    api_token: str,
    host: str,
) -> str:
    return get_variable_value(host, api_token, "pay_cc_webhook_secret_key")
