import contextlib

from pymongo import errors

from snowfall.project.junction.service.offers import aggregator, offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import consumer
from snowfall.stdlib.transport.amqp import types as amqp_types


class OfferImporter(object):
    def __init__(
        self,
        consumer_obj: consumer.Consumer,
        trip_offers: offers.TripOfferRepository,
        offer_aggregator: aggregator.OfferAggregator,
        redis: types.Client[str],
    ):
        self._consumer = consumer_obj
        self._offers = trip_offers
        self._aggregator = offer_aggregator
        self._redis = redis

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        message: amqp_types.Message[amqp_pb2.TripOfferSearchResult],
    ) -> None:
        redis_lock = "results:{0}".format(message.body.offer_search_id)

        async with self._redis.lock(redis_lock, timeout=10):
            await self._aggregator.aggregate(message.body)

            with contextlib.suppress(errors.DuplicateKeyError):
                await self._offers.insert(message.body.offer)
