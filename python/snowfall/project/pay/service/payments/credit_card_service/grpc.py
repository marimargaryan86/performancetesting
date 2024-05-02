from collections.abc import Mapping

import grpc
from google.protobuf.json_format import MessageToDict

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import (
    credit_card_pb2,
    credit_card_pb2_grpc,
)
from snowfall.stdlib import money
from snowfall.stdlib.transport.grpc import service


class CreditCardPaymentService(
    service.Service,
    credit_card_pb2_grpc.CreditCardPaymentServiceServicer,
):
    def __init__(
        self,
        providers: Mapping[str, interfaces.CreditCardProvider],
        reseller_to_provider: Mapping[str, str],
    ):
        self._providers = providers
        self._reseller_to_provider = reseller_to_provider

    def get_name(self) -> str:
        return credit_card_pb2.DESCRIPTOR.services_by_name[
            "CreditCardPaymentService"
        ].full_name

    def register(self, server: grpc.aio.Server) -> None:
        credit_card_pb2_grpc.add_CreditCardPaymentServiceServicer_to_server(
            self,
            server,
        )

    async def GetCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.GetCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.GetCreditCardPaymentResponse:
        payment = self._provider(request.reseller_id).get_credit_card_payment(
            request.payment_id,
        )
        if not payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not found",
            )
        return credit_card_pb2.GetCreditCardPaymentResponse(payment=payment)

    async def CreateCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CreateCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CreateCreditCardPaymentResponse:
        payment = self._provider(request.reseller_id).create_credit_card_payment(
            request.payment,
        )
        if not payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not created",
            )

        return credit_card_pb2.CreateCreditCardPaymentResponse(payment=payment)

    async def UpdateCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.UpdateCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.UpdateCreditCardPaymentResponse:
        metadata = MessageToDict(request.metadata, preserving_proto_field_name=True)
        updated_payment = self._provider(
            request.reseller_id,
        ).update_credit_card_payment(
            request.payment_id,
            money.from_protobuf(request.amount)
            if request.amount.ListFields()
            else None,
            receipt_email=request.receipt_email or None,
            metadata=metadata or None,
        )

        if not updated_payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not found",
            )

        return credit_card_pb2.UpdateCreditCardPaymentResponse(payment=updated_payment)

    async def ProcessCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.ProcessCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.ProcessCreditCardPaymentResponse:
        payment_method = self._provider(request.reseller_id).get_payment_method(
            request.payment_id,
        )
        if not payment_method:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment method not found",
            )

        processed_payment = self._provider(
            request.reseller_id,
        ).process_credit_card_payment(
            request.payment_id,
            payment_method,
        )
        if not processed_payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not processed",
            )

        return credit_card_pb2.ProcessCreditCardPaymentResponse(
            payment=processed_payment,
        )

    async def GetCreditCardHolder(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.GetCreditCardHolderRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.GetCreditCardHolderResponse:
        credit_card_holder, signature = await self._provider(
            request.reseller_id,
        ).get_credit_card_holder(
            request.credit_card_holder_id,
        )

        return credit_card_pb2.GetCreditCardHolderResponse(
            credit_card_holder=credit_card_holder,
            signature=signature,
        )

    async def CreateCreditCardHolder(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CreateCreditCardHolderRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CreateCreditCardHolderResponse:
        credit_card_holder, signature = await self._provider(
            request.reseller_id,
        ).create_credit_card_holder(
            request.user_id,
            request.credit_card_holder,
        )

        return credit_card_pb2.CreateCreditCardHolderResponse(
            credit_card_holder=credit_card_holder,
            signature=signature,
        )

    async def CancelCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CancelCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CancelCreditCardPaymentResponse:
        credit_card_payment = self._provider(
            request.reseller_id,
        ).cancel_credit_card_payment(
            request.payment_id,
        )
        if not credit_card_payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not canceled",
            )

        return credit_card_pb2.CancelCreditCardPaymentResponse(
            payment=credit_card_payment,
        )

    async def CaptureCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CaptureCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CaptureCreditCardPaymentResponse:
        credit_card_payment = self._provider(
            request.reseller_id,
        ).capture_credit_card_payment(
            request.payment_id,
        )
        if not credit_card_payment:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Payment not captured",
            )

        return credit_card_pb2.CaptureCreditCardPaymentResponse(
            payment=credit_card_payment,
        )

    async def CreateRefund(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CreateRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CreateRefundResponse:
        refund = self._provider(request.reseller_id).create_refund(
            amount=request.amount,
            credit_card_payment_id=request.credit_card_payment_id,
        )

        if refund is None:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT)

        return credit_card_pb2.CreateRefundResponse(refund=refund)

    async def GetRefund(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.GetRefundRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.GetRefundResponse:
        refund = self._provider(request.reseller_id).get_refund(
            external_reference_id=request.refund_id,
        )

        if refund is None:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return credit_card_pb2.GetRefundResponse(refund=refund)

    async def CreateSetupClientSecret(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CreateSetupClientSecretRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CreateSetupClientSecretResponse:
        signature = await self._provider(  # type: ignore[attr-defined]
            request.reseller_id,
        ).get_setup_client_secret(
            request.customer_id,
        )

        if not signature:
            await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="Client secret is not created",
            )

        return credit_card_pb2.CreateSetupClientSecretResponse(signature=signature)

    def _provider(self, reseller_id: str) -> interfaces.CreditCardProvider:
        return self._providers.get(
            self._reseller_to_provider.get(reseller_id, ""),
            self._providers["stripe"],
        )
