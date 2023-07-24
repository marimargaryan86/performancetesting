from snowfall.project.junction.plus.adapter import (
    configuration_vectors as configuration_vectors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    subscribers as subscribers_adapter,
)
from snowfall.project.junction.plus.notification_channels.whatsapp import Channel
from snowfall.project.junction.plus.service.notification_center import validators
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class NotificationEventImporter(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[models_pb2.NotificationEvent],
        configuration_vectors: configuration_vectors_adapter.Client,
        subscribers: subscribers_adapter.Client,
        whatsapp_provider: Channel,
    ):
        self._consumer = consumer_obj
        self._configuration_vectors = configuration_vectors
        self._subscribers = subscribers
        self._whatsapp_provider = whatsapp_provider
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.NotificationEvent],
    ) -> None:
        validators.validate_notifications(message.body)
        subscriber = await self._subscribers.get(
            subscriber_id=message.body.receiver_id,
        )
        configuration_vector = await self._configuration_vectors.get(
            reseller_id=message.body.sender_id,
        )

        self._logger.warning(str(configuration_vector))
        self._logger.warning(str(subscriber))

        await self._whatsapp_provider.send_order_confirmation(
            sender_configuration=configuration_vector,
            receiver=subscriber,
            order=message.body.body,
        )

        self._logger.warning(str(message.body))
