import datetime
import random
import uuid
from collections.abc import AsyncIterator
from typing import Sequence, cast

import pydantic

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib import service
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport import amqp


class _OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class MockClient(object):
    async def search(
        self,
        search: offers_pb2.TripOfferSearchTask,
    ) -> AsyncIterator[offers_pb2.TripOfferResult]:
        yield offers_pb2.TripOfferResult(
            id=str(uuid.uuid4()),
            offer_search_id=search.offer_search_id,
            segment_ids=[segment.id for segment in search.search.segments],
            expires_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(
                    tz=datetime.timezone.utc,
                )
                + datetime.timedelta(minutes=15),
            ),
            schedules=[
                models_pb2.Schedule(
                    id="123",
                    name="Uppsala - Stockholm",
                    stops=[
                        models_pb2.Stop(
                            id="234",
                            departure_at=protobuf.datetime_to_protobuf(
                                datetime.datetime.now(tz=datetime.timezone.utc),
                            ),
                            point=models_pb2.Point(
                                ref="foobar",
                                name="Uppsala",
                                time_zone="Europe/Stockholm",
                            ),
                            order=1,
                        ),
                        models_pb2.Stop(
                            id="234",
                            arrival_at=protobuf.datetime_to_protobuf(
                                datetime.datetime.now(tz=datetime.timezone.utc)
                                + datetime.timedelta(hours=1),
                            ),
                            point=models_pb2.Point(
                                ref="foobar",
                                name="Stockholm",
                                time_zone="Europe/Stockholm",
                            ),
                            order=1,
                        ),
                    ],
                    agency_name="Trips Delight",
                    source_ref="456",
                    type=models_pb2.Schedule.Type.TYPE_AIR,
                ),
            ],
            price=models_pb2.Price(
                amount=123,
                currency="EUR",
            ),
        )


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        client: MockClient,
    ):
        self._consumer = consumer
        self._producer = producer
        self._client = client

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(offers_pb2.TripOfferSearchTask, message.body)

        async for offer_result in self._client.search(search):
            await self._producer.publish(offer_result, routing_key="offers.result.trip")

        await message.ack()


async def _offers(app: service.Application[_OffersSettings]) -> None:
    async with amqp.Connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        consumer = TripSearchConsumer(
            consumer=await amqp.create_consumer(
                conn=connection,
                exchange_name="offers",
                queue_name="{0}_offers".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=await amqp.create_producer(
                conn=connection,
                exchange_name="offers",
            ),
            client=MockClient(),
        )

        await consumer.consume()


if __name__ == "__main__":
    entrypoint = service.Entrypoint(name="mock")

    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=_offers,
            settings_class=_OffersSettings,
        ),
    )
