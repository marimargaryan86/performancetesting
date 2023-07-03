from snowfall.project.junction.plus.adapter import (
    configuration_vectors as configuration_vectors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    subscribers as subscribers_adapter,
)
from snowfall.project.junction.plus.adapter import validation
from snowfall.project.junction.plus.service.notification_center import validators
from snowfall.project.junction.plus.service.notification_center.v1alpha import amqp_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class NotificationEventImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.NotificationEvent],
        configuration_vectors: configuration_vectors_adapter.Client,
        subscribers: subscribers_adapter.Client,
    ):
        self._consumer = consumer_obj
        self._configuration_vectors = configuration_vectors
        self._subscribers = subscribers
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.NotificationEvent],
    ) -> None:
        try:
            validators.validate_notifications(message.body)
        except* validation.ProtobufValidationError:
            self._logger.warning("Validation Error", exc_info=True)
        else:
            subscriber = await self._subscribers.get(
                subscriber_id=message.body.receiver_id,
            )
            configuration_vector = await self._configuration_vectors.get(
                reseller_id=message.body.sender_id,
            )

            self._logger.warning(str(configuration_vector))
            self._logger.warning(str(subscriber))

        self._logger.warning(str(message.body))
