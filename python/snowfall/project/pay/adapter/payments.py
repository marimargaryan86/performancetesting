from __future__ import annotations

import abc
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.payments.v1alpha import (
    models_pb2,
    payments_pb2,
    payments_pb2_grpc,
)
from snowfall.stdlib import sequence, string
from snowfall.stdlib.format import protobuf


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(self, payment: models_pb2.Payment) -> models_pb2.Payment:
        """Create a payment resource."""

    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.Payment:
        """Fetch a payment resource."""

    @abc.abstractmethod
    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> payments_pb2.ListPaymentsResponse:
        """Fetch all payment resources."""

    @abc.abstractmethod
    async def update_state(
        self,
        payment_id: str,
        status: str,
        failure_message: str,
    ) -> bool:
        """Update a payment resource."""


class DictClient(Client):
    def __init__(self, payments: Sequence[models_pb2.Payment]):
        self._payments = {payment.id: payment for payment in payments}

    async def create(self, payment: models_pb2.Payment) -> models_pb2.Payment:
        new_payment = models_pb2.Payment()
        new_payment.CopyFrom(payment)
        new_payment.id = string.uuid()
        self._payments[new_payment.id] = new_payment

        return new_payment

    async def get(self, payment_id: str) -> models_pb2.Payment:
        try:
            return self._payments[payment_id]
        except KeyError as err:
            raise errors.NotFoundError() from err

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> payments_pb2.ListPaymentsResponse:
        page = sequence.paginate(
            sequence=list(self._payments.values()),
            cursor=cursor,
            limit=limit,
        )

        return payments_pb2.ListPaymentsResponse(
            payments=page.sequence,
            next_page_token=page.cursor,
        )

    async def update_state(
        self,
        external_reference_id: str,
        status: str,
        failure_message: str,
    ) -> bool:
        for ind, val_pay in self._payments.items():
            if val_pay.external_reference_id == external_reference_id:
                val_pay.status = protobuf.slug_to_enum_value(
                    models_pb2.Status,
                    status,
                )
                val_pay.status_description = failure_message
                self._payments[ind] = val_pay
                return True
        return False


class GrpcClient(Client):
    def __init__(
        self,
        payments: payments_pb2_grpc.PaymentsServiceStub,
        timeout: int = 10,
    ):
        self._payments = payments
        self._timeout = timeout

    async def create(self, payment: models_pb2.Payment) -> models_pb2.Payment:
        response = await errors.handle_grpc_errors(
            self._payments.CreatePayment(
                payments_pb2.CreatePaymentRequest(
                    payment=payment,
                ),
            ),
        )

        return response.payment

    async def get(self, payment_id: str) -> models_pb2.Payment:
        response = await errors.handle_grpc_errors(
            self._payments.GetPayment(
                payments_pb2.GetPaymentRequest(id=payment_id),
                timeout=self._timeout,
            ),
        )

        return response.payment

    async def find(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> payments_pb2.ListPaymentsResponse:
        # TODO: handle INVALID_ARGUMENT
        request = payments_pb2.ListPaymentsRequest(
            page_token=cursor or "",
        )
        if limit is not None:
            request.page_size = limit

        return await errors.handle_grpc_errors(
            self._payments.ListPayments(request, timeout=self._timeout),
        )

    async def update_state(
        self,
        external_reference_id: str,
        status: str,
        failure_message: str,
    ) -> bool:
        response = await self._payments.UpdatePaymentState(
            payments_pb2.UpdatePaymentStateRequest(
                external_reference_id=external_reference_id,
                status=protobuf.slug_to_enum_value(
                    models_pb2.Status,
                    status,
                ),
                status_description=failure_message,
            ),
        )
        return response.is_success
