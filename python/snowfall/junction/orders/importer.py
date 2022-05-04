from typing import cast

from snowfall.junction.orders import orders
from snowfall.junction.orders.v1alpha import models_pb2
from snowfall.stdlib.transport import amqp


class OrderImporter(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        order_repository: orders.OrderRepository,
    ):
        self._consumer = consumer
        self._orders = order_repository

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        order_result = cast(models_pb2.OrderResult, message.body)
        await self._orders.update_offer_status(
            order_id=order_result.order_id,
            offer_id=order_result.offer_id,
            status=order_result.status,
            raw_data=order_result.raw_data,
        )
