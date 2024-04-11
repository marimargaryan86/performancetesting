from abc import abstractmethod
from collections.abc import Mapping

from snowfall.project.pay.service.payments.v1 import (
    credit_card_models_pb2,
    invoice_models_pb2,
)
from snowfall.stdlib import money


class CreditCardProvider:
    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name."""

    @abstractmethod
    def get_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Get payment detail."""

    @abstractmethod
    def create_credit_card_payment(
        self,
        payment: credit_card_models_pb2.CreditCardPayment,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Create payment."""

    @abstractmethod
    def update_credit_card_payment(
        self,
        payment_id: str,
        amount: money.Money | None,
        receipt_email: str | None,
        metadata: Mapping[str, str] | None,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Update payment."""

    @abstractmethod
    def cancel_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Cancel credit card payment."""

    @abstractmethod
    def capture_credit_card_payment(
        self,
        payment_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Capture credit card payment."""

    @abstractmethod
    def process_credit_card_payment(
        self,
        payment_id: str,
        payment_method_id: str,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Confirm credit card payment."""

    @abstractmethod
    async def get_credit_card_holder(
        self,
        user_id: str,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Get credit card holder detail."""

    @abstractmethod
    async def create_credit_card_holder(
        self,
        user_id: str,
        credit_card_holder: credit_card_models_pb2.CreditCardHolder,
    ) -> tuple[credit_card_models_pb2.CreditCardHolder, str]:
        """Create credit card holder."""

    @abstractmethod
    def create_refund(
        self,
        amount: int,
        credit_card_payment_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Create refund."""

    @abstractmethod
    def get_refund(
        self,
        external_reference_id: str,
    ) -> credit_card_models_pb2.Refund | None:
        """Get refund."""

    @abstractmethod
    def get_payment_method(self, payment_id: str) -> str:
        """Get payment method's id."""


class InvoiceProvider:
    @abstractmethod
    def create_account(
        self,
        name: str,
        email: str,
    ) -> invoice_models_pb2.InvoiceAccount:
        """Create account."""

    @abstractmethod
    def create_invoice(
        self,
        invoice_account_id: str,
        days_until_due: int,
        currency: str,
    ) -> invoice_models_pb2.Invoice | None:
        """Create invoice."""

    @abstractmethod
    def create_invoice_item(
        self,
        invoice_account_id: str,
        invoice_id: str,
        amount: money.Money,
        description: str,
    ) -> invoice_models_pb2.InvoiceItem | None:
        """Create an invoice item."""

    @abstractmethod
    def finalize_invoice(self, invoice_id: str) -> bool:
        """Finalize invoice."""
