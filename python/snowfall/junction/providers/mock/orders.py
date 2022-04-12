import random
from collections.abc import AsyncIterator
from typing import Sequence, cast

import pydantic

from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.orders.v1alpha import orders_pb2
from snowfall.stdlib import service
from snowfall.stdlib.transport import amqp


class OrdersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class OrdersMockClient(object):
    async def search(
        self,
        order: orders_pb2.OrderTask,
    ) -> AsyncIterator[orders_pb2.OrderResult]:
        for offer in order.offers:
            yield orders_pb2.OrderResult(
                order_id=order.order_id,
                offer_id=offer.id,
                status=offers_pb2.Offer.Status.STATUS_CONFIRMED,
            )


class OrdersConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        client: OrdersMockClient,
    ):
        self._consumer = consumer
        self._producer = producer
        self._client = client

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(orders_pb2.OrderTask, message.body)

        async for order_result in self._client.search(search):
            await self._producer.publish(
                order_result,
                routing_key="orders.result.offer",
            )

        await message.ack()


async def orders(app: service.Application[OrdersSettings]) -> None:
    async with amqp.Connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        consumer = OrdersConsumer(
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="orders",
                queue_name="{0}_orders".format(app.name),
                routing_key="orders.offers",
            ),
            producer=await amqp.create_producer(
                conn=connection,
                exchange_name="orders",
            ),
            client=OrdersMockClient(),
        )

        await consumer.consume()
