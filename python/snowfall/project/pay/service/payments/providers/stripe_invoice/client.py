import stripe

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import invoice_models_pb2


class StripeInvoice(interfaces.InvoiceProvider):
    def __init__(
        self,
        stripe_version: str,
        stripe_key: str,
    ):
        self._stripe_version = stripe_version
        self._stripe_key = stripe_key
        stripe.api_key = stripe_key

    def create_account(
        self,
        name: str,
        email: str,
    ) -> invoice_models_pb2.InvoiceAccount:
        """Create Customer in stripe."""
        customer = stripe.Customer.create(
            email=email,
            name=name,
        )

        return invoice_models_pb2.InvoiceAccount(
            email=email,
            name=name,
            id=customer.id,
        )

    def create_invoice(
        self,
        invoice_account_id: str,
        days_until_due: int,
    ) -> invoice_models_pb2.Invoice | None:
        try:
            stripe_invoice = stripe.Invoice.create(
                customer=invoice_account_id,
                collection_method="send_invoice",
                days_until_due=days_until_due,
            )
        except stripe.StripeError:
            return None

        return invoice_models_pb2.Invoice(
            id=stripe_invoice.id,  # type: ignore[arg-type]
        )
