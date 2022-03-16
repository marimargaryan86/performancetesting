import collections
import itertools
import uuid

from snowfall.junction.offers import offers
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence import redis

OfferBuckets = dict[str, list[str]]


def generate_offer_aggregates(
    offer_buckets: OfferBuckets,
) -> list[offers_pb2.OfferAggregate]:
    return [
        offers_pb2.OfferAggregate(
            id=str(uuid.uuid4()),
            offer_result_ids=aggregate,
        )
        for aggregate in itertools.product(*offer_buckets.values())
    ]


class OfferBucketRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
    ):
        self._redis = redis_client

    async def add_offer(self, offer: offers_pb2.TripOfferResult) -> None:
        key = ":".join([offer.offer_search_id, offer.segment_ids[0]])
        bucket = self._redis.list_(key)
        await bucket.push(offer.id)
        await redis.put_expires_at_if_greater(
            self._redis,
            bucket,
            protobuf.protobuf_to_datetime(offer.expires_at),
        )

        bucket_list = self._redis.set_(offer.offer_search_id)
        await bucket_list.add(key)
        await redis.put_expires_at_if_greater(
            self._redis,
            bucket_list,
            protobuf.protobuf_to_datetime(offer.expires_at),
        )

    async def get_offer_buckets(self, offer_search_id: str) -> dict[str, list[str]]:
        bucket_list = self._redis.set_(offer_search_id)
        buckets = collections.defaultdict(list)

        async for bucket_name in bucket_list.to_iterable():
            bucket = self._redis.list_(bucket_name)

            async for offer_id in bucket.to_iterable():
                buckets[bucket_name.split(":")[1]].append(offer_id)

        return buckets


class OfferAggregator(object):
    def __init__(
        self,
        offer_searches: offers.OfferSearchRepository,
        offer_buckets: OfferBucketRepository,
        offer_aggregates: offers.OfferAggregateRepository,
    ):
        self._searches = offer_searches
        self._buckets = offer_buckets
        self._aggregates = offer_aggregates

    async def aggregate(self, offer: offers_pb2.TripOfferResult) -> None:
        offer_search = await self._searches.find_by_id(offer.offer_search_id)

        if not offer_search:
            return

        buckets = await self._get_buckets(offer)

        await self._buckets.add_offer(offer)

        for segment in offer_search.trip.segments:
            if segment.id not in buckets:
                return

        for aggregate in generate_offer_aggregates(buckets):
            await self._aggregates.insert(aggregate)

    async def _get_buckets(self, offer: offers_pb2.TripOfferResult) -> OfferBuckets:
        buckets = await self._buckets.get_offer_buckets(offer.offer_search_id)
        buckets[offer.segment_ids[0]] = [offer.id]

        return buckets
