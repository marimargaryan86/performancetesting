import grpc

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import (
    credit_card_pb2,
    credit_card_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class CreditCardPaymentService(
    service.Service,
    credit_card_pb2_grpc.CreditCardPaymentServiceServicer,
):
    def __init__(self, provider: interfaces.CreditCardProvider):
        self._provider = provider

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
        payment = self._provider.get_credit_card_payment(request.payment_id)
        return credit_card_pb2.GetCreditCardPaymentResponse(payment=payment)

    async def CreateCreditCardPayment(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.CreateCreditCardPaymentRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.CreateCreditCardPaymentResponse:
        payment = self._provider.create_credit_card_payment(
            request.payment,
        )
        return credit_card_pb2.CreateCreditCardPaymentResponse(payment=payment)

    async def GetCreditCardHolder(  # type: ignore[override] # noqa: N802
        self,
        request: credit_card_pb2.GetCreditCardHolderRequest,
        context: grpc.aio.ServicerContext,
    ) -> credit_card_pb2.GetCreditCardHolderResponse:
        credit_card_holder, signature = await self._provider.get_credit_card_holder(
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
        credit_card_holder, signature = await self._provider.create_credit_card_holder(
            request.user_id,
            request.credit_card_holder,
        )

        return credit_card_pb2.CreateCreditCardHolderResponse(
            credit_card_holder=credit_card_holder,
            signature=signature,
        )
