import datetime
import random
import uuid
from collections.abc import AsyncIterator
from typing import Sequence, cast

import pydantic

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.providers.v1alpha import offers_pb2 as provider_offers_pb2
from snowfall.stdlib import service
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport import amqp


class OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class OffersMockClient(object):
    async def search(
        self,
        search: offers_pb2.TripOfferSearchTask,
    ) -> AsyncIterator[provider_offers_pb2.GroupedOffer]:
        yield provider_offers_pb2.GroupedOffer(
            id=str(uuid.uuid4()),
            offer_search_id=search.offer_search_id,
            offers=[
                provider_offers_pb2.Offer(
                    id="FOO",
                    segments=[
                        provider_offers_pb2.OfferSegment(
                            id=segment.id,
                        )
                        for segment in search.search.segments
                    ],
                    price=models_pb2.Price(
                        amount=1337,
                        currency="EUR",
                    ),
                ),
            ],
            segments=[
                provider_offers_pb2.Segment(
                    id=segment.id,
                    legs=[
                        provider_offers_pb2.Leg(
                            id=leg.id,
                            origin=leg.origin,
                            destination=leg.destination,
                            departure_at=leg.departure_at,
                            arrival_at=leg.arrival_at,
                        ),
                    ],
                    vehicle=provider_offers_pb2.Vehicle(
                        number="123",
                        equipment="B52",
                    ),
                    operator="SK",
                    vendor="BA",
                    terminal="5",
                )
                for segment in search.search.segments
                for leg in segment.legs
            ],
            expires_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(
                    tz=datetime.timezone.utc,
                )
                + datetime.timedelta(minutes=15),
            ),
        )


class TripSearchConsumer(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        producer: amqp.Producer,
        client: OffersMockClient,
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


async def offers(app: service.Application[OffersSettings]) -> None:
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
            client=OffersMockClient(),
        )

        await consumer.consume()
