from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.stdlib.transport import amqp


class OrderProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(self, order: orders_pb2.Order) -> None:
        await self._producer.publish(
            orders_pb2.OrderTask(
                order_id=order.id,
                offers=order.offers,
            ),
            "orders.offers",
        )
