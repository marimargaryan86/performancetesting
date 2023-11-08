import datetime

import grpc

from snowfall.project.pay.service.payments.repositories import PaymentsRepository
from snowfall.project.pay.service.payments.v1 import (
    models_pb2,
    payments_pb2,
    payments_pb2_grpc,
)
from snowfall.stdlib import money, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.grpc import service
from snowfall.vendor.currency_cloud.client import PaymentClient
from snowfall.vendor.currency_cloud.models.payment import PaymentRequest


class PaymentsService(service.Service, payments_pb2_grpc.PaymentsServiceServicer):
    def __init__(
        self,
        payments_repository: PaymentsRepository,
        payment_client: PaymentClient,
    ):
        self._payments_repository = payments_repository
        self._payment_client = payment_client
        self._default_page_size = 20

    def get_name(self) -> str:
        return payments_pb2.DESCRIPTOR.services_by_name["PaymentsService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        payments_pb2_grpc.add_PaymentsServiceServicer_to_server(self, server)

    async def CreatePayment(  # type: ignore[override] # noqa: N802
        self,
        request: payments_pb2.CreatePaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> payments_pb2.CreatePaymentResponse:
        payment = request.payment
        amount = money.from_protobuf(payment.amount)

        cc_payment = await self._payment_client.create_payment(
            PaymentRequest(
                currency=amount.currency.code,
                beneficiary_id=payment.beneficiary_id,
                amount=str(amount),
                reason=payment.reason,
                reference=payment.reference,
                unique_request_id=string.uuid(),
                payment_type=payment.payment_type,
                payment_date=(
                    protobuf.protobuf_to_date(payment.payment_due_date)
                    if payment.payment_due_date.ByteSize()
                    else None
                ),
            ),
        )

        payment.MergeFrom(
            models_pb2.Payment(
                id=string.uuid(),
                status=models_pb2.Status.STATUS_PENDING,
                external_reference_id=cc_payment.identifier,
                created_at=protobuf.datetime_to_protobuf(
                    datetime.datetime.now(tz=datetime.UTC),
                ),
                created_by=payment.created_by,
                payment_due_date=protobuf.date_to_protobuf(cc_payment.payment_date),
            ),
        )

        payment = await self._payments_repository.insert(payment)

        return payments_pb2.CreatePaymentResponse(payment=payment)

    async def GetPayment(  # type: ignore[override] # noqa: N802
        self,
        request: payments_pb2.GetPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> payments_pb2.GetPaymentResponse:
        payment = await self._payments_repository.find_by_id(request.id)

        if payment is None:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return payments_pb2.GetPaymentResponse(payment=payment)

    async def ListPayments(  # type: ignore[override] # noqa: N802
        self,
        request: payments_pb2.ListPaymentsRequest,
        context: grpc.aio.ServicerContext,
    ) -> payments_pb2.ListPaymentsResponse:
        payments = await self._payments_repository.find(
            cursor=request.page_token,
        )
        payments.limit(request.page_size or self._default_page_size)

        return payments_pb2.ListPaymentsResponse(
            payments=[payment async for payment in payments],
            next_page_token=await payments.cursor(),
        )

    async def UpdatePaymentState(  # type: ignore[override] # noqa: N802
        self,
        request: payments_pb2.UpdatePaymentStateRequest,
        context: grpc.aio.ServicerContext,
    ) -> payments_pb2.UpdatePaymentStateResponse:
        is_updated = await self._payments_repository.update_state(
            request.external_reference_id,
            request.status,
            request.status_description,
        )

        return payments_pb2.UpdatePaymentStateResponse(
            is_success=is_updated,
        )
