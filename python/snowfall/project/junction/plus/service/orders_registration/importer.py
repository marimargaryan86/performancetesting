from snowfall.project.junction.plus.adapter import errors
from snowfall.project.junction.plus.service.notification_center.v1alpha import (
    amqp_pb2 as notif_amqp_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2_grpc as notifications_pb2_grpc,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.project.junction.plus.service.orders_registration import validators
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types


class OrderImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.IncomingOrder],
        producer_obj: producer.Producer,
        orders: notifications_pb2_grpc.OrderServiceStub,
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
            channel=notif_amqp_pb2.NotificationEvent.CHANNEL_WHATSAPP,
        )
        await self._producer.publish(notification_event, "plus.events")

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.IncomingOrder],
    ) -> None:
        try:
            await validators.validate_orders(message.body)
        except* validators.ProtobufValidationError:
            self._logger.warning("Validation Error", exc_info=True)
        else:
            response = await errors.handle_grpc_errors(
                self._orders.CreateOrder(
                    notifications_pb2.CreateOrderRequest(
                        reseller_id=message.body.reseller_id,
                        external_ref_id=message.body.external_ref_id,
                        contact_details=message.body.contact_details,
                        passengers=message.body.passengers,
                        bookings=message.body.bookings,
                    ),
                    timeout=self._timeout,
                ),
            )
            await self.publish_event(response.order)
            self._logger.warning(str(response.order))
