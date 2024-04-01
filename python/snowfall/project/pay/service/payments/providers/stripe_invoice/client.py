import stripe

from snowfall.project.pay.service.payments.providers import interfaces
from snowfall.project.pay.service.payments.v1 import invoice_models_pb2
from snowfall.stdlib import money


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
        currency: str,
    ) -> invoice_models_pb2.Invoice | None:
        payment_methods = ["card"]
        if currency.lower() == "gbp":
            payment_methods.append(
                "customer_balance",
            )
        try:
            stripe_invoice = stripe.Invoice.create(
                customer=invoice_account_id,
                collection_method="send_invoice",
                days_until_due=days_until_due,
                currency=currency,
                payment_settings={
                    "payment_method_types": payment_methods,  # type: ignore[typeddict-item]
                },
            )
        except stripe.StripeError:
            return None

        return invoice_models_pb2.Invoice(
            id=stripe_invoice.id,  # type: ignore[arg-type]
        )

    def create_invoice_item(
        self,
        invoice_account_id: str,
        invoice_id: str,
        amount: money.Money,
        description: str,
    ) -> invoice_models_pb2.InvoiceItem | None:
        try:
            invoice_item = stripe.InvoiceItem.create(
                customer=invoice_account_id,
                amount=amount.amount,
                currency=amount.currency.code,
                invoice=invoice_id,
                description=description,
            )
        except stripe.StripeError:
            return None
        return invoice_models_pb2.InvoiceItem(
            id=invoice_item.id,
            invoice_account_id=invoice_account_id,
            invoice_id=invoice_id,
            amount=amount.protobuf(),
            description=description,
        )

    def finalize_invoice(self, invoice_id: str) -> bool:
        try:
            stripe.Invoice.finalize_invoice(invoice_id)
        except stripe.StripeError:
            return False

        return True
