from snowfall.project.junction.go.adapter import orders
from snowfall.project.junction.go.adapter.errors import UnhandledError
from snowfall.project.junction.go.service.orders.v1.orders_pb2 import Status
from snowfall.project.junction.go.service.zendesk_webhook.v1 import amqp_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types

status_map: dict[str, Status.ValueType] = {
    "Solved": Status.STATUS_REFUND_DUE,
    "Rejected": Status.STATUS_REJECTED,
    "No Refund": Status.STATUS_NO_REFUND,
}


class TicketEventConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TicketChangedEvent],
        orders_client: orders.Client,
    ):
        self._consumer = consumer_obj
        self._orders_client = orders_client
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TicketChangedEvent],
    ) -> None:
        if message.body.status not in status_map:
            self._logger.error(
                "Failed to process TicketChangeEvent, unknown status received",
                status=message.body.status,
            )
            return

        try:
            await self._orders_client.handle_cancellation_ticket_completed(
                ticket_id=message.body.ticket_id,
                status=status_map[message.body.status],
            )
        except UnhandledError:
            self._logger.exception(
                "Failed to process TicketChangeEvent",
                body=message.body,
            )
