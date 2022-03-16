from typing import cast

from snowfall.junction.offers import offers
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib.transport import amqp


class OfferImporter(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        trip_offers: offers.TripOfferRepository,
    ):
        self._consumer = consumer
        self._offers = trip_offers

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search = cast(offers_pb2.TripOfferResult, message.body)

        if await self._offers.insert(search):
            await message.ack()
        else:
            await message.nack()
