from snowfall.project.pay.adapter.payments import GrpcClient
from snowfall.project.pay.service.webhooks.models.payment import Payment


class PaymentState(object):
    def __init__(self, payment_client: GrpcClient, payment: Payment):
        self._payment_client = payment_client
        self._payment = payment

    async def payment_ready_to_send_notification(self) -> bool:
        return await self._update_payment()

    async def payment_released_notification(self) -> bool:
        return await self._update_payment()

    async def payment_compliance_failed_notification(self) -> bool:
        return await self._update_payment()

    async def payment_failed_notification(self) -> bool:
        return await self._update_payment()

    async def run(self, notification_type: str) -> bool:
        if hasattr(self, notification_type):  # noqa: WPS421
            return await getattr(self, notification_type)()
        raise NotImplementedError("{0} is not implemented".format(notification_type))

    async def _update_payment(self) -> bool:
        return await self._payment_client.update_state(
            self._payment.identifier,
            self._payment.status,
            self._payment.failure_reason,
        )
