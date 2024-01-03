import abc

from snowfall.project.pay.service.payments.v1 import (
    credit_card_models_pb2,
    credit_card_pb2,
    credit_card_pb2_grpc,
)
from snowfall.stdlib import money


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_credit_card_holder(
        self,
        credit_card_holder_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get credit card holder."""

    @abc.abstractmethod
    async def create_credit_card_holder(
        self,
        user_id: str,
        email: str,
        name: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Create Credit Card holder."""

    @abc.abstractmethod
    async def create_credit_card_payment(
        self,
        amount: money.Money,
        credit_card_holder_id: str,
        enable_automatic_payment_method: bool,  # noqa: FBT001
        capture_method: str = "manual",
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Create credit card payment."""


class GrpcClient(Client):
    def __init__(
        self,
        credit_card_payment_stub: credit_card_pb2_grpc.CreditCardPaymentServiceStub,
        timeout: int = 10,
    ):
        self._client = credit_card_payment_stub
        self._timeout = timeout

    async def get_credit_card_holder(
        self,
        user_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        credit_card_holder_request = credit_card_pb2.CreateCreditCardHolderRequest(
            user_id=user_id,
        )
        credit_card_holder_response = await self._client.GetCreditCardHolder(
            credit_card_holder_request,
            self._timeout,
        )
        return (
            credit_card_holder_response.credit_card_hodler,
            credit_card_holder_response.signature,
        )

    async def create_credit_card_holder(
        self,
        user_id: str,
        email: str,
        name: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        credit_card_holder_request = credit_card_pb2.CreateCreditCardHolderRequest(
            credit_card_holder=credit_card_models_pb2.CreditCardHolder(
                email=email,
                name=name,
            ),
            user_id=user_id,
        )
        credit_card_holder_response = await self._client.GetCreditCardHolder(
            credit_card_holder_request,
            self._timeout,
        )
        return (
            credit_card_holder_response.credit_card_hodler,
            credit_card_holder_response.signature,
        )

    async def create_credit_card_payment(
        self,
        amount: money.Money,
        credit_card_holder_id: str,
        enable_automatic_payment_method: bool,  # noqa: FBT001
        capture_method: str = "manual",
    ) -> credit_card_models_pb2.CreditCardPayment:
        payment_request = credit_card_pb2.CreateCreditCardPaymentRequest(
            payment=credit_card_models_pb2.CreditCardPayment(
                amount=amount.protobuf(),
                credit_card_holder_id=credit_card_holder_id,
                capture_method=capture_method,
                enable_automatic_payment_method=enable_automatic_payment_method,
            ),
        )

        payment_response = await self._client.CreateCreditCardPayment(
            payment_request,
            self._timeout,
        )

        return payment_response.payment
