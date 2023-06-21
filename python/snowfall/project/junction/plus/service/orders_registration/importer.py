from pymongo.errors import PyMongoError

from snowfall.project.junction.plus.service.notification_center.v1alpha import amqp_pb2
from snowfall.project.junction.plus.service.orders_registration import (
    orders_registration,
    validators,
)
from snowfall.project.junction.plus.service.orders_registration.v1alpha import (
    models_pb2,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types


class OrderImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.IncomingOrder],
        producer_obj: producer.Producer,
        order_repository: orders_registration.OrderRepository,
        subscriber_repository: orders_registration.SubscriberRepository,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._orders = order_repository
        self._subscribers = subscriber_repository
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def publish_event(
        self,
        order: models_pb2.PersistedOrder,
    ) -> None:
        notification_event = amqp_pb2.NotificationEvent(
            sender_id=order.reseller_id,
            receiver_id=order.subscriber_id,
            body=order,
            channel=amqp_pb2.NotificationEvent.CHANNEL_WHATSAPP,
        )
        await self._producer.publish(notification_event, "plus.events")

    async def _process_message(
        self,
        message: types.Message[models_pb2.IncomingOrder],
    ) -> None:
        try:
            await validators.validate_orders(message.body)
        except* validators.ProtobufValidationError:
            self._logger.warning("Validation Error", exc_info=True)
        else:
            try:
                subscriber = await self._subscribers.get_or_create(message.body)
            except PyMongoError:
                subscriber = None
                self._logger.exception(
                    "Failed to create a subscriber for registration",
                    email=message.body.contact_details.email,
                )
            if subscriber:
                try:
                    persisted_order = await self._orders.create(
                        message.body,
                        subscriber,
                    )
                except PyMongoError:
                    self._logger.exception(
                        "Failed to create a order for registration",
                        reseller_id=message.body.reseller_id,
                        external_ref_id=message.body.external_ref_id,
                    )
                else:
                    await self.publish_event(persisted_order)
        self._logger.warning(str(message.body))
