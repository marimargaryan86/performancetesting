from snowfall.project.junction.plus.adapter import orders as orders_adapter
from snowfall.project.junction.plus.service.notification_center.v1alpha import (
    amqp_pb2 as notif_amqp_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.project.junction.plus.service.orders_registration import validators
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types


class OrderImporter(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.IncomingOrder],
        producer_obj: producer.Producer,
        orders: orders_adapter.Client,
        timeout: int = 10,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._orders = orders
        self._timeout = timeout
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def publish_event(
        self,
        order: models_pb2.PersistedOrder,
    ) -> None:
        notification_event = notif_amqp_pb2.NotificationEvent(
            sender_id=order.reseller_id,
            receiver_id=order.subscriber_id,
            body=order,
            event_type=notif_amqp_pb2.NotificationEvent.TYPE_ORDER_CONFIRMATION,
            channel=notifications_models_pb2.Channel.CHANNEL_WHATSAPP,
        )
        await self._producer.publish(notification_event, "plus.events")

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.IncomingOrder],
    ) -> None:
        validators.validate_orders(message.body)
        persisted_order = await self._orders.create(
            notifications_pb2.CreateOrderRequest(
                reseller_id=message.body.reseller_id,
                external_ref_id=message.body.external_ref_id,
                booking_reference=message.body.booking_reference,
                contact_details=message.body.contact_details,
                passengers=message.body.passengers,
                bookings=message.body.bookings,
            ),
        )
        await self.publish_event(persisted_order)

        self._logger.warning(str(persisted_order))
