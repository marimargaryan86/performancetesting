import asyncio

from snowfall.junction.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport import amqp


class OrderProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(self, order: models_pb2.Order) -> None:
        await asyncio.gather(
            self._producer.publish(
                amqp_pb2.PlaceOrderTask(
                    order=order,
                    offer_id=offer.id,
                ),
                "orders.offers",
            )
            for offer in order.offers
        )
