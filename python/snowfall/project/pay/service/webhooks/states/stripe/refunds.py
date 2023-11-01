import stripe
from stripe.stripe_object import StripeObject

from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.go.service.orders.v1 import (
    models_pb2 as orders_models_pb2,
)
from snowfall.project.pay.adapter import refunds, transactions
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()


class RefundsState(object):
    def __init__(
        self,
        stripe_api_key: str,
        refunds_client: refunds.Client,
        transactions_client: transactions.Client,
        orders_client: orders.Client,
    ):
        self.stripe_api_key = stripe_api_key
        self._refunds_client = refunds_client
        self._transactions_client = transactions_client
        self._orders_client = orders_client

    async def charge_refunded(
        self,
        stripe_refund: stripe.Refund,
    ) -> bool:
        update_status = await self._update_refund(
            stripe_refund.refunds.data[0].id,
            stripe_refund.status,
        )
        if update_status and stripe_refund.status == "succeeded":
            await self._update_booking_cancellation_status(
                stripe_refund.refunds.data[0].id,
            )

        return update_status

    async def run(self, event: StripeObject) -> bool:
        event_type = event.type.replace(".", "_")
        if hasattr(self, event_type):  # noqa: WPS421
            logger.info("Occurred event", event_name=event_type)
            return await getattr(self, event_type)(event.data.object)
        logger.error("Unhandled event", event_name=event_type)
        return False

    async def _update_booking_cancellation_status(
        self,
        stripe_refund_id: str,
    ) -> None:
        refund = await self._refunds_client.get(
            identifier=stripe_refund_id,
            selector="external_reference_id",
        )
        transaction = await self._transactions_client.get(
            identifier=refund.transaction_id,
        )
        booking_cancellation = (
            await self._orders_client.get_booking_cancellation_by_booking_id(
                booking_id=transaction.external_reference_id,
                reseller_id="",
            )
        )
        await self._orders_client.update_booking_cancellations(
            orders_models_pb2.BookingCancellation(
                id=booking_cancellation.id,
                status=orders_models_pb2.BookingCancellation.Status.STATUS_REFUND_ISSUED,
            ),
        )

    async def _update_refund(
        self,
        stripe_refund_id: str,
        stripe_refund_status: str,
    ) -> bool:
        return await self._refunds_client.update_status(
            stripe_refund_id,
            stripe_refund_status,
        )
