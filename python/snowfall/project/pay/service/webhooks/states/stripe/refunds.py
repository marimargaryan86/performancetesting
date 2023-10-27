import stripe
from stripe.stripe_object import StripeObject

from snowfall.project.pay.adapter.refunds import Client
from snowfall.stdlib.logging import stdout

logger = stdout.get_logger()


class RefundsState(object):
    def __init__(
        self,
        stripe_api_key: str,
        refunds_client: Client,
    ):
        self.stripe_api_key = stripe_api_key
        self._refunds_client = refunds_client

    async def charge_refunded(
        self,
        stripe_refund: stripe.Refund,
    ) -> bool:
        return await self._update_refund(
            stripe_refund.id,
            stripe_refund.status,
        )

    async def run(self, event: StripeObject) -> bool:
        event_type = event.type.replace(".", "_")
        if hasattr(self, event_type):  # noqa: WPS421
            logger.info("Occurred event", event_name=event_type)
            return await getattr(self, event_type)(event.data.object)
        logger.error("Unhandled event", event_name=event_type)
        return False

    async def _update_refund(
        self,
        stripe_refund_id: str,
        stripe_refund_status: str,
    ) -> bool:
        return await self._refunds_client.update_status(
            stripe_refund_id,
            stripe_refund_status,
        )
