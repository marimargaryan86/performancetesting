import datetime
import itertools
from collections.abc import AsyncIterator

import pydantic

from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offers_pb2
from snowfall.stdlib import money, service, string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.transport.amqp import consumer, producer, types


class OffersSettings(service.Settings):
    amqp_dsn: pydantic.AnyUrl


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
                    price=money.from_string(
                        string_amount="13.37",
                        currency=money.Currency("EUR"),
                    ).protobuf(),
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
        consumer_obj: consumer.Consumer[amqp_pb2.TripOfferSearchTask],
        producer_obj: producer.Producer,
        client: OffersMockClient,
    ):
        self._consumer = consumer_obj
        self._producer = producer_obj
        self._client = client

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: types.Message[amqp_pb2.TripOfferSearchTask],
    ) -> None:
        async for offer_result in self._client.search(message.body):
            await self._producer.publish(
                amqp_pb2.TripOfferSearchResult(
                    offer_search_id=message.body.offer_search_id,
                    offer=offer_result,
                ),
                routing_key="offers.result.trip",
            )

        await message.ack()


async def offers(app: service.Application[OffersSettings]) -> None:
    async with types.Connection(app.settings.amqp_dsn) as connection:
        consumer_obj = TripSearchConsumer(
            consumer_obj=consumer.Consumer(
                connection=connection,
                queue_name="{0}_offers".format(app.name),
                binds=[(types.Exchange("offers"), "offers.search.trip")],
            ),
            producer_obj=producer.Producer(
                connection=connection,
                exchange=types.Exchange("offers"),
            ),
            client=OffersMockClient(),
        )

        await consumer_obj.consume()
