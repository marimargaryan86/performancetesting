from abc import abstractmethod

from snowfall.project.pay.service.payments.v1 import credit_card_models_pb2
from snowfall.stdlib import money


class CreditCardProvider(object):
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
    ) -> credit_card_models_pb2.CreditCardPayment:
        """Create payment."""

    @abstractmethod
    def update_credit_card_payment(
        self,
        payment_id: str,
        amount: money.Money,
    ) -> credit_card_models_pb2.CreditCardPayment | None:
        """Update payment."""

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
