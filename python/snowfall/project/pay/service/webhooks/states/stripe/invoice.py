import stripe

from snowfall.project.junction.go.adapter import errors
from snowfall.project.pay.adapter import transactions
from snowfall.project.pay.service.transactions.v1.models_pb2 import InvoiceStatus
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()


class InvoiceState:
    def __init__(
        self,
        stripe_api_key: str,
        transactions_client: transactions.Client,
    ):
        self.stripe_api_key = stripe_api_key
        self._transaction_client = transactions_client

    async def invoice_marked_uncollectible(
        self,
        stripe_invoice: stripe.Invoice,
    ) -> bool:
        try:
            return await self._transaction_client.update_invoice_status(
                stripe_invoice.id,  # type: ignore[arg-type]
                InvoiceStatus.INVOICE_STATUS_FAILED,
            )
        except errors.NotFoundError:
            return False

    async def invoice_voided(self, stripe_invoice: stripe.Invoice) -> bool:
        return await self._transaction_client.update_invoice_status(
            stripe_invoice.id,  # type: ignore[arg-type]
            InvoiceStatus.INVOICE_STATUS_FAILED,
        )

    async def invoice_paid(self, stripe_invoice: stripe.Invoice) -> bool:
        return await self._transaction_client.update_invoice_status(
            stripe_invoice.id,  # type: ignore[arg-type]
            InvoiceStatus.INVOICE_STATUS_SUCCEEDED,
        )

    async def run(self, event: stripe.StripeObject) -> bool:
        event_type = event["type"].replace(".", "_")
        if hasattr(self, event_type):  # noqa: WPS421
            logger.info("Occurred event", event_name=event_type)
            return await getattr(self, event_type)(event["data"]["object"])
        logger.error("Unhandled event", event_name=event_type)
        return False
