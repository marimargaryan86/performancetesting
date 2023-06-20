from snowfall.project.junction.plus.service.orders_registration import (
    orders_registration,
    validators,
)
from snowfall.project.junction.plus.service.orders_registration.v1alpha import (
    models_pb2,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, types


class OrderImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer[models_pb2.IncomingOrder],
        order_repository: orders_registration.OrderRepository,
        subscriber_repository: orders_registration.SubscriberRepository,
    ):
        self._consumer = consumer_obj
        self._orders = order_repository
        self._subscribers = subscriber_repository
        self._logger = stdout.get_logger()

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[models_pb2.IncomingOrder],
    ) -> None:
        try:
            await validators.validate_orders(message.body)
        except* validators.ProtobufValidationError:
            self._logger.warning("Validation Error", exc_info=True)
        else:
            subscriber = await self._subscribers.get_or_create(message.body)
            await self._orders.create(message.body, subscriber)

        self._logger.warning(str(message.body))
