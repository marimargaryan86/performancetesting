from typing import cast

from snowfall.project.junction.service.offers import aggregator, offers
from snowfall.project.junction.service.offers.v1alpha import models_pb2
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
        offer = cast(models_pb2.OfferGroup, message.body)

        await self._offers.insert(offer)
        await self._aggregator.aggregate(offer)
