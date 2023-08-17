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
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer, types


class NotificationEventImporter(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[models_pb2.NotificationEvent],
        configuration_vectors: configuration_vectors_adapter.Client,
        subscribers: subscribers_adapter.Client,
        channels: states.Channels,
        redis_client: redis.Client[str],
    ):
        self._consumer = consumer_obj
        self._configuration_vectors = configuration_vectors
        self._subscribers = subscribers
        self._channels = channels
        self._redis = redis_client
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

        self._logger.warning(str(configuration_vector))
        self._logger.warning(str(subscriber))
        fun = protobuf.enum_value_to_slug(
            enum_descriptor=models_pb2.NotificationEvent.Type.DESCRIPTOR,
            enum_value=message.body.event_type,
        ).replace("-", "_")
        sid = await self._channels.run(
            message.body.channel,
            fun,
            configuration_vector,
            subscriber,
            message.body,
        )
        session = self._redis.hash_("message_id_order_id")
        await session.put(sid, message.body.body.id)
