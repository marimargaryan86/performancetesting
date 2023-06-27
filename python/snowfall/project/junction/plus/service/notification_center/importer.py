from snowfall.project.junction.plus.service.notification_center import validators
from snowfall.project.junction.plus.service.notification_center.v1alpha import amqp_pb2
from snowfall.project.junction.plus.service.orders_registration.validators import (
    ProtobufValidationError,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class NotificationEventImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.NotificationEvent],
    ):
        self._consumer = consumer_obj
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.NotificationEvent],
    ) -> None:
        try:
            await validators.validate_notifications(message.body)
        except* ProtobufValidationError:
            self._logger.warning("Validation Error", exc_info=True)
        self._logger.warning(str(message.body))
