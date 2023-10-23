from snowfall.project.junction.go.service.zendesk_webhook.v1 import amqp_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class TicketEventConsumer(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.TicketChangedEvent],
    ):
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TicketChangedEvent],
    ) -> None:
        self._logger.info(
            "Received new event for ticket %s",
            message.body.ticket_id,
        )
