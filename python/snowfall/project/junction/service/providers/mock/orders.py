import copy
import random
from collections.abc import AsyncIterator
from typing import Sequence, cast

import pydantic

from snowfall.project.junction.service.orders.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib import money, service
from snowfall.stdlib.transport import amqp


class OrdersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class OrdersMockClient(object):
    async def book(
        self,
        task: amqp_pb2.PlaceOrderTask,
    ) -> AsyncIterator[models_pb2.Booking]:
        new_booking = copy.deepcopy(task.booking)

        new_booking.MergeFrom(
            models_pb2.Booking(
                status=models_pb2.Booking.STATUS_CONFIRMED,
                provider_name="Mock",
                total_price=money.from_string(
                    string_amount="13.37",
                    currency=money.Currency("EUR"),
                ).protobuf(),
                trip_result=models_pb2.TripBooking(
                    record_locator="ABCDEF",
                ),
            ),
        )

        yield new_booking


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
        search = cast(amqp_pb2.PlaceOrderTask, message.body)

        async for order_result in self._client.book(search):
            await self._producer.publish(
                order_result,
                routing_key="orders.result.offer",
            )

        await message.ack()


async def orders(app: service.Application[OrdersSettings]) -> None:
    async with await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        consumer = OrdersConsumer(
            consumer=amqp.Consumer(
                connection=connection,
                exchange=amqp.Exchange("orders"),
                queue_name="{0}_orders".format(app.name),
                routing_key="orders.offers",
            ),
            producer=amqp.Producer(
                connection=connection,
                exchange=amqp.Exchange("orders"),
            ),
            client=OrdersMockClient(),
        )

        await consumer.consume()
