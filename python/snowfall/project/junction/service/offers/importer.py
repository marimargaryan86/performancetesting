import contextlib
from typing import cast

from pymongo import errors

from snowfall.project.junction.service.offers import aggregator, offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport import amqp


class OfferImporter(object):
    def __init__(
        self,
        consumer: amqp.Consumer,
        trip_offers: offers.TripOfferRepository,
        offer_aggregator: aggregator.OfferAggregator,
        redis: types.Client[str],
    ):
        self._consumer = consumer
        self._offers = trip_offers
        self._aggregator = offer_aggregator
        self._redis = redis

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(self, message: amqp.Message) -> None:
        search_result = cast(amqp_pb2.TripOfferSearchResult, message.body)
        redis_lock = "results:{0}".format(search_result.offer_search_id)

        async with self._redis.lock(redis_lock):
            await self._aggregator.aggregate(search_result)

            with contextlib.suppress(errors.DuplicateKeyError):
                await self._offers.insert(search_result.offer)
