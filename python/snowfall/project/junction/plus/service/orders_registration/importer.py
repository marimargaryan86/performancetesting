from snowfall.project.junction.plus.adapter import (
    errors as errors_adapter,
)
from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)
from snowfall.project.junction.plus.adapter import (
    orders as orders_adapter,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    grpc_pb2 as notifications_pb2,
)
from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2
from snowfall.project.junction.plus.service.notifications.v1alpha import (
    models_pb2 as notifications_models_pb2,
)
from snowfall.project.junction.plus.service.orders_registration import (
    flight_stats,
    validators,
)
from snowfall.project.junction.plus.service.orders_registration.v1alpha import amqp_pb2
from snowfall.stdlib import string
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, producer, types


class OrderImporter(object):
    def __init__(  # noqa: WPS211
        self,
        consumer_obj: consumer.Consumer[amqp_pb2.IncomingOrder],
        producer_obj: producer.Producer,
        orders: orders_adapter.Client,
        monitoring_rules: monitoring_rules_adapter.Client,
        flight_stats_client: flight_stats.Client,
        timeout: int = 10,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._orders = orders
        self._monitoring_rules = monitoring_rules
        self._flight_stats_client = flight_stats_client
        self._timeout = timeout
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def publish_event(
        self,
        order: models_pb2.PersistedOrder,
    ) -> None:
        notification_event = models_pb2.NotificationEvent(
            sender_id=order.reseller_id,
            receiver_id=order.subscriber_id,
            body=order,
            event_type=models_pb2.NotificationEvent.TYPE_ORDER_CONFIRMATION,
            channel=notifications_models_pb2.Channel.CHANNEL_WHATSAPP,
        )
        await self._producer.publish(notification_event, "plus.events")

    async def _process_message(  # noqa: WPS217
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
        for booking in persisted_order.bookings:
            try:
                existing_rule = await self._monitoring_rules.get_by_booking(booking)
            except errors_adapter.NotFoundError:
                monitoring_rule_id = string.uuid()
                rule = await self._flight_stats_client.create_monitoring_rule(
                    booking,
                    monitoring_rule_id,
                )
                await self._monitoring_rules.create(
                    notifications_models_pb2.MonitoringRule(
                        id=monitoring_rule_id,
                        ext_rule_id=rule["rule"]["id"],
                        booking=booking,
                        subscriber_ids=[persisted_order.subscriber_id],
                    ),
                )
            else:
                if persisted_order.subscriber_id not in existing_rule.subscriber_ids:
                    existing_rule.subscriber_ids.append(persisted_order.subscriber_id)
                await self._monitoring_rules.update(monitoring_rule=existing_rule)
        self._logger.warning(str(persisted_order))
