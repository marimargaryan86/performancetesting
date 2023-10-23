from snowfall.project.junction.plus.adapter import (
    configuration_vectors as configuration_vectors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    subscribers as subscribers_adapter,
)
from snowfall.project.junction.plus.service.notification_center import (
    states,
    validators,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class NotificationEventImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.NotificationEvent],
        configuration_vectors: configuration_vectors_adapter.Client,
        subscribers: subscribers_adapter.Client,
        channels: states.Channels,
    ):
        self._consumer = consumer_obj
        self._configuration_vectors = configuration_vectors
        self._subscribers = subscribers
        self._channels = channels
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
            identifier=message.body.sender_id,
        )
        if message.body.channel:
            channel = message.body.channel
        else:
            channel = configuration_vector.channel
        fun = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.NotificationEvent.Type.DESCRIPTOR,
            enum_value=message.body.event_type,
        ).replace("-", "_")
        await self._channels.run(
            channel,
            fun,
            configuration_vector,
            subscriber,
            message.body,
        )
