import random
import uuid
from typing import Sequence, cast

import pydantic

from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.service import RunnableService, Task, make_runnable_service
from snowfall.transport import amqp


class _GrpcSettings(pydantic.BaseSettings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
    ):
        self._consumer = consumer
        self._producer = producer

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(offers_pb2.TripOfferSearchTask, message.body)
        offer_result = offers_pb2.TripOfferResult(
            id=str(uuid.uuid4()),
            offer_search_id=search.offer_search_id,
        )

        await self._producer.publish(offer_result, routing_key="offers.result.trip")
        await message.ack()


async def _offers(service: RunnableService) -> None:
    settings = _GrpcSettings()

    async with amqp.Connection(random.choice(settings.amqp_dsn)) as connection:  # nosec
        consumer = TripSearchConsumer(
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="offers",
                queue_name="{0}_offers".format(service.name),
                routing_key="offers.search.trip",
            ),
            producer=await amqp.create_producer(
                conn=connection,
                exchange_name="offers",
            ),
        )

        await consumer.consume()


if __name__ == "__main__":
    _service = make_runnable_service(
        name="mock",
        tasks=(Task(command="offers", method=_offers),),
    )
    _service.run()
