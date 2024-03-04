from collections.abc import Mapping

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money, string


class MockStripe(interfaces.CreditCardProvider):
    def __init__(
        self,
    ) -> None:
        self._credit_card_payments = {}  # type: ignore[var-annotated]
        self._credit_card_holders = {}  # type: ignore[var-annotated]
        self._users_to_credit_card_holder_id = {}  # type: ignore[var-annotated]
        self._refunds = {}  # type: ignore[var-annotated]

    @property
    def name(self) -> str:
        return "mock-stripe"

    def get_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Retrieve payment intent."""
        return self._credit_card_payments.get(payment_id)

    def create_credit_card_payment(
        self,
        payment: credit_card_models_pb2.CreditCardPayment,
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Create payment intent in stripe."""
        payment.id = string.uuid()
        payment.secret = string.uuid()
        payment.status = "requires_capture"

        self._credit_card_payments[payment.id] = payment

        return payment

    def update_credit_card_payment(
        self,
        payment_id: str,
        amount: money.Money | None,
        receipt_email: str | None,
        metadata: Mapping[str, str] | None,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
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
        return None

    def cancel_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            self._credit_card_payments[payment_id].status = "canceled"
            return self._credit_card_payments[payment_id]
        return None

    def capture_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        credit_card_payment = self._credit_card_payments.get(payment_id)
        if credit_card_payment:
            self._credit_card_payments[payment_id].status = "succeeded"
            return self._credit_card_payments[payment_id]
        return None

    async def get_credit_card_holder(
        self,
        credit_card_holder_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get customer id and ephemeral key."""
        return self._credit_card_holders.get(
            self._users_to_credit_card_holder_id.get(credit_card_holder_id),
            credit_card_models_pb2.CreditCardHolder(),
        ), "ephemeral_key"

    async def create_credit_card_holder(
        self,
        user_id: str,
        credit_card_holder: credit_card_models_pb2.CreditCardHolder,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Create Customer in stripe and save the id in the DB."""
        credit_card_holder.id = string.uuid()
        credit_card_holder.version = "stripe_version"
        self._credit_card_holders[user_id] = credit_card_holder
        self._users_to_credit_card_holder_id[credit_card_holder.id] = user_id
        return credit_card_holder, "ephemeral_key"

    def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Create refund in stripe."""
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

    def get_refund(
        self,
        external_reference_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Get refund from stripe."""
        refund = self._refunds.get(external_reference_id)
        if refund:
            return refund
        return None
