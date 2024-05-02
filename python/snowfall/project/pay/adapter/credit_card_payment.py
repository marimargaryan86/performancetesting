import abc
from collections.abc import Mapping
from typing import Literal

from google.protobuf.json_format import ParseDict

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.service.payments.v1 import (
    credit_card_models_pb2,
    credit_card_pb2,
    credit_card_pb2_grpc,
)
from snowfall.stdlib import money, string


class Client(abc.ABC):
    @abc.abstractmethod
    async def get_credit_card_holder(
        self,
        user_id: str,
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get credit card holder."""

    @abc.abstractmethod
    async def create_credit_card_holder(
        self,
        user_id: str,
        email: str,
        name: str,
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Create Credit Card holder."""

    @abc.abstractmethod
    async def get_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Get Credit Card Payment."""

    @abc.abstractmethod
    async def create_credit_card_payment(
        self,
        amount: money.Money,
        credit_card_holder_id: str,
        enable_automatic_payment_method: bool,  # noqa: FBT001
        reseller_id: str = "",
        capture_method: str = "manual",
        setup_future_usage: str = "on_session",
        allow_redirect: Literal["always", "never"] = "always",
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Create credit card payment."""

    @abc.abstractmethod
    async def update_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
        amount: money.Money | None = None,
        receipt_email: str = "",
        metadata: Mapping[str, str] | None = None,
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Update credit card payment."""

    @abc.abstractmethod
    async def cancel_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Cancel the credit card payment."""

    @abc.abstractmethod
    async def capture_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Capture the credit card payment."""

    @abc.abstractmethod
    async def process_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Execute payment."""

    @abc.abstractmethod
    async def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        """Create refund."""

    @abc.abstractmethod
    async def get_refund(
        self,
        external_reference_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        """Get refund."""

    @abc.abstractmethod
    async def get_setup_client_secret(
        self,
        customer_id: str,
    ) -> str:
        """Get setup client secret."""


class DictClient(Client):
    def __init__(self) -> None:
        self._credit_card_payments = {}  # type: ignore[var-annotated]
        self._credit_card_holders = {}  # type: ignore[var-annotated]
        self._refunds = {}  # type: ignore[var-annotated]

    async def get_credit_card_holder(
        self,
        user_id: str,
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        return self._credit_card_holders.get(
            user_id,
            credit_card_models_pb2.CreditCardHolder(),
        ), "ephemeral_key"

    async def create_credit_card_holder(
        self,
        user_id: str,
        email: str,
        name: str,
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        credit_card_holder_id = string.uuid()
        credit_card_holder = credit_card_models_pb2.CreditCardHolder(
            id=credit_card_holder_id,
            email=email,
            name=name,
        )
        self._credit_card_holders[user_id] = credit_card_holder

        return credit_card_holder, "ephemeral_key"

    async def get_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            return credit_card_payment
        raise errors.NotFoundError()

    async def create_credit_card_payment(
        self,
        amount: money.Money,
        credit_card_holder_id: str,
        enable_automatic_payment_method: bool,  # noqa: FBT001
        reseller_id: str = "",
        capture_method: str = "manual",
        setup_future_usage: str = "on_session",
        allow_redirect: Literal["always", "never"] = "always",
    ) -> credit_card_models_pb2.CreditCardPayment:
        credit_card_payment_id = string.uuid()
        credit_card_payment = credit_card_models_pb2.CreditCardPayment(
            id=credit_card_payment_id,
            amount=amount.protobuf(),
            capture_method=capture_method,
            credit_card_holder_id=credit_card_holder_id,
            enable_automatic_payment_method=enable_automatic_payment_method,
            secret="Payment_Secret",  # noqa: S106
            setup_future_usage=setup_future_usage,
            allow_redirect=allow_redirect,
        )
        self._credit_card_payments[credit_card_payment_id] = credit_card_payment
        return credit_card_payment

    async def update_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
        amount: money.Money | None = None,
        receipt_email: str = "",
        metadata: Mapping[str, str] | None = None,
    ) -> credit_card_models_pb2.CreditCardPayment:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            new_credit_card_payment = credit_card_models_pb2.CreditCardPayment(
                id=credit_card_payment.id,
                amount=credit_card_payment.amount
                if amount is None
                else amount.protobuf(),
                capture_method=credit_card_payment.capture_method,
                credit_card_holder_id=credit_card_payment.credit_card_holder_id,
                enable_automatic_payment_method=credit_card_payment.enable_automatic_payment_method,
                secret=credit_card_payment.secret,
                status=credit_card_payment.status,
            )
            self._credit_card_payments[payment_id] = new_credit_card_payment
            return new_credit_card_payment
        raise errors.NotFoundError()

    async def cancel_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            self._credit_card_payments[payment_id].status = "canceled"
            return self._credit_card_payments[payment_id]

        raise errors.NotFoundError()

    async def capture_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            self._credit_card_payments[payment_id].status = "succeeded"
            return self._credit_card_payments[payment_id]

        raise errors.NotFoundError()

    async def process_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        if payment_id not in self._credit_card_payments:
            raise errors.NotFoundError()

        return self._credit_card_payments[payment_id]

    async def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        external_reference_id = string.uuid()
        refund = credit_card_models_pb2.Refund(
            external_reference_id=external_reference_id,
            credit_card_payment_id=string.uuid(),
            amount=money.Money(
                amount=amount,
                currency=money.Currency("USD"),
            ).protobuf(),
        )
        self._refunds[external_reference_id] = refund

        return refund

    async def get_refund(
        self,
        external_reference_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        refund = self._refunds.get(external_reference_id)
        if refund:
            return refund
        raise errors.NotFoundError()

    async def get_setup_client_secret(
        self,
        customer_id: str,
    ) -> str:
        return "client_secret"


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
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        credit_card_holder_request = credit_card_pb2.GetCreditCardHolderRequest(
            credit_card_holder_id=user_id,
            reseller_id=reseller_id,
        )
        credit_card_holder_response = await self._client.GetCreditCardHolder(
            credit_card_holder_request,
            timeout=self._timeout,
        )
        return (
            credit_card_holder_response.credit_card_holder,
            credit_card_holder_response.signature,
        )

    async def create_credit_card_holder(
        self,
        user_id: str,
        email: str,
        name: str,
        reseller_id: str = "",
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        credit_card_holder_request = credit_card_pb2.CreateCreditCardHolderRequest(
            credit_card_holder=credit_card_models_pb2.CreditCardHolder(
                email=email,
                name=name,
            ),
            user_id=user_id,
            reseller_id=reseller_id,
        )
        credit_card_holder_response = await self._client.CreateCreditCardHolder(
            credit_card_holder_request,
            timeout=self._timeout,
        )
        return (
            credit_card_holder_response.credit_card_holder,
            credit_card_holder_response.signature,
        )

    async def get_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        get_payment_request = credit_card_pb2.GetCreditCardPaymentRequest(
            payment_id=payment_id,
            reseller_id=reseller_id,
        )

        payment_response = await errors.handle_grpc_errors(
            self._client.GetCreditCardPayment(
                get_payment_request,
                timeout=self._timeout,
            ),
        )

        return payment_response.payment

    async def create_credit_card_payment(
        self,
        amount: money.Money,
        credit_card_holder_id: str,
        enable_automatic_payment_method: bool,  # noqa: FBT001
        reseller_id: str = "",
        capture_method: str = "manual",
        setup_future_usage: str = "on_session",
        allow_redirect: Literal["always", "never"] = "always",
    ) -> credit_card_models_pb2.CreditCardPayment:
        payment_request = credit_card_pb2.CreateCreditCardPaymentRequest(
            payment=credit_card_models_pb2.CreditCardPayment(
                amount=amount.protobuf(),
                credit_card_holder_id=credit_card_holder_id,
                capture_method=capture_method,
                enable_automatic_payment_method=enable_automatic_payment_method,
                setup_future_usage=setup_future_usage,
                allow_redirect=allow_redirect,
            ),
            reseller_id=reseller_id,
        )

        payment_response = await errors.handle_grpc_errors(
            self._client.CreateCreditCardPayment(
                payment_request,
                timeout=self._timeout,
            ),
        )

        return payment_response.payment

    async def update_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
        amount: money.Money | None = None,
        receipt_email: str = "",
        metadata: Mapping[str, str] | None = None,
    ) -> credit_card_models_pb2.CreditCardPayment:
        proto_metadata = None
        if metadata:
            proto_metadata = ParseDict(
                metadata,
                credit_card_models_pb2.PaymentMetaData(),
            )
        update_payment_request = credit_card_pb2.UpdateCreditCardPaymentRequest(
            payment_id=payment_id,
            amount=None if amount is None else amount.protobuf(),
            receipt_email=receipt_email,
            metadata=proto_metadata,
            reseller_id=reseller_id,
        )

        updated_payment = await errors.handle_grpc_errors(
            self._client.UpdateCreditCardPayment(
                update_payment_request,
                timeout=self._timeout,
            ),
        )

        return updated_payment.payment

    async def cancel_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        cancel_response = await errors.handle_grpc_errors(
            self._client.CancelCreditCardPayment(
                credit_card_pb2.CancelCreditCardPaymentRequest(
                    payment_id=payment_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )
        return cancel_response.payment

    async def capture_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        capture_response = await errors.handle_grpc_errors(
            self._client.CaptureCreditCardPayment(
                credit_card_pb2.CancelCreditCardPaymentRequest(
                    payment_id=payment_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )
        return capture_response.payment

    async def process_credit_card_payment(
        self,
        payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.CreditCardPayment:
        process_response = await errors.handle_grpc_errors(
            self._client.ProcessCreditCardPayment(
                credit_card_pb2.ProcessCreditCardPaymentRequest(
                    payment_id=payment_id,
                    reseller_id=reseller_id,
                ),
            ),
        )

        return process_response.payment

    async def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        response = await errors.handle_grpc_errors(
            self._client.CreateRefund(
                credit_card_pb2.CreateRefundRequest(
                    amount=amount,
                    credit_card_payment_id=credit_card_payment_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.refund

    async def get_refund(
        self,
        external_reference_id: str,
        reseller_id: str = "",
    ) -> credit_card_models_pb2.Refund:
        response = await errors.handle_grpc_errors(
            self._client.GetRefund(
                credit_card_pb2.GetRefundRequest(
                    refund_id=external_reference_id,
                    reseller_id=reseller_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.refund

    async def get_setup_client_secret(
        self,
        customer_id: str,
    ) -> str:
        response = await errors.handle_grpc_errors(
            self._client.CreateSetupClientSecret(
                credit_card_pb2.CreateSetupClientSecretRequest(
                    customer_id=customer_id,
                ),
                timeout=self._timeout,
            ),
        )

        return response.signature
