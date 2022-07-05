from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib.transport import amqp


class OrderProducer(object):
    def __init__(self, producer: amqp.Producer):
        self._producer = producer

    async def publish(self, order: models_pb2.Order) -> None:
        for order_result in order.order_results:
            await self._producer.publish(
                amqp_pb2.PlaceOrderTask(
                    order=order,
                    offer_id=order_result.offer_id,
                ),
                "orders.offers",
            )
