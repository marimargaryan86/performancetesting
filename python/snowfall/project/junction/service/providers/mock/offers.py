import datetime
import itertools
import random
from collections.abc import AsyncIterator
from typing import Sequence, cast

import pydantic

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.stdlib import service, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.v1alpha import models_pb2


class OffersSettings(service.Settings):
    amqp_dsn: Sequence[pydantic.AnyUrl]


class OffersMockClient(object):
    async def search(
        self,
        search: amqp_pb2.TripOfferSearchTask,
    ) -> AsyncIterator[offers_pb2.OfferGroup]:
        segments = itertools.chain(*[tr.segments for tr in search.search.trips])

        yield offers_pb2.OfferGroup(
            id=string.uuid(),
            offers=[
                offers_pb2.Offer(
                    id="FOO",
                    segment_details=[
                        offers_pb2.OfferSegmentDetails(
                            id=segment.id,
                        )
                        for segment in segments
                    ],
                    price=models_pb2.Price(
                        amount=1337,
                        currency="EUR",
                    ),
                ),
            ],
            segments=[
                offers_pb2.OfferSegment(
                    id=segment.id,
                    legs=[
                        offers_pb2.OfferSegmentLeg(
                            id=leg.id,
                            origin=leg.origin,
                            destination=leg.destination,
                            departure_at=leg.departure_at,
                            arrival_at=leg.arrival_at,
                        ),
                    ],
                    vehicle=offers_pb2.Vehicle(
                        number="123",
                        equipment="B52",
                    ),
                    operator="SK",
                    vendor="BA",
                    terminal="5",
                )
                for segment in segments
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
        search = cast(amqp_pb2.TripOfferSearchTask, message.body)

        async for offer_result in self._client.search(search):
            await self._producer.publish(
                amqp_pb2.TripOfferSearchResult(
                    offer_search_id=search.offer_search_id,
                    offer=offer_result,
                ),
                routing_key="offers.result.trip",
            )

        await message.ack()


async def offers(app: service.Application[OffersSettings]) -> None:
    async with await amqp.create_connection(
        random.choice(app.settings.amqp_dsn),  # nosec
    ) as connection:
        consumer = TripSearchConsumer(
            consumer=amqp.Consumer(
                connection=connection,
                exchange=amqp.Exchange("offers"),
                queue_name="{0}_offers".format(app.name),
                routing_key="offers.search.trip",
            ),
            producer=amqp.Producer(
                connection=connection,
                exchange=amqp.Exchange("offers"),
            ),
            client=OffersMockClient(),
        )

        await consumer.consume()
