from unittest import mock

import grpc
import pytest

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay import fixtures
from snowfall.project.pay.adapter import payments
from snowfall.project.pay.service.payments.v1 import (
    payments_pb2,
    payments_pb2_grpc,
)


class TestDictClient(object):
    async def test_single_payment_is_retrievable(
        self,
        payments_client: payments.Client,
    ) -> None:
        payment = await payments_client.get(fixtures.PAYMENTS[0])
        assert payment.id == fixtures.PAYMENTS[0]

    async def test_missing_payment_throws_error(
        self,
        payments_client: payments.Client,
    ) -> None:
        with pytest.raises(errors.NotFoundError):
            await payments_client.get(fixtures.NOT_FOUND)

    async def test_multiple_payments_are_retrievable(
        self,
        payments_client: payments.Client,
    ) -> None:
        found_payments = await payments_client.find(limit=100)
        assert len(found_payments.payments) == 2

    async def test_single_payment_is_creatable(
        self,
        payments_client: payments.Client,
    ) -> None:
        payment = await payments_client.get(fixtures.PAYMENTS[0])
        payment = await payments_client.create(payment)
        new_payment = await payments_client.get(payment.id)
        assert payment.id == new_payment.id


class TestGrpcClient(object):
    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.NOT_FOUND,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.NotFoundError,
            ),
            (
                grpc.aio.AioRpcError(
                    code=grpc.StatusCode.UNKNOWN,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                ),
                errors.UnhandledError,
            ),
        ],
    )
    async def test_error_responses(
        self,
        error: grpc.aio.AioRpcError,
        expected: type[Exception],
    ) -> None:
        stub = mock.create_autospec(payments_pb2_grpc.PaymentsServiceStub)
        stub.GetPayment = mock.AsyncMock(side_effect=error)
        client = payments.GrpcClient(stub)
        with pytest.raises(expected):
            await client.get(fixtures.NOT_FOUND)

    async def test_single_payment_is_retrievable(self) -> None:
        proto = fixtures.generate_payment(fixtures.PAYMENTS[0])
        stub = mock.create_autospec(payments_pb2_grpc.PaymentsServiceStub)
        stub.GetPayment = mock.AsyncMock(
            return_value=payments_pb2.GetPaymentResponse(payment=proto),
        )
        client = payments.GrpcClient(stub)
        payment = await client.get(fixtures.PAYMENTS[0])
        assert payment.id == fixtures.PAYMENTS[0]

    async def test_multiple_payments_are_retrievable(self) -> None:
        response = payments_pb2.ListPaymentsResponse(
            payments=[
                fixtures.generate_payment(fixtures.PAYMENTS[0]),
                fixtures.generate_payment(fixtures.PAYMENTS[1]),
            ],
        )
        stub = mock.create_autospec(payments_pb2_grpc.PaymentsServiceStub)
        stub.ListPayments = mock.AsyncMock(return_value=response)
        client = payments.GrpcClient(stub)
        found_payments = await client.find(limit=100)
        assert len(found_payments.payments) == 2
