from typing import cast

from snowfall.junction.offers import aggregator, offers
from snowfall.junction.providers.v1alpha import offers_pb2
from snowfall.stdlib.transport import amqp


class OfferImporter(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        trip_offers: offers.TripOfferRepository,
        offer_aggregator: aggregator.OfferAggregator,
    ):
        self._consumer = consumer
        self._offers = trip_offers
        self._aggregator = offer_aggregator

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        offer = cast(offers_pb2.GroupedOffer, message.body)

        await self._offers.insert(offer)

        await self._aggregator.aggregate(offer)
