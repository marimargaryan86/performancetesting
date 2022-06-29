import collections
import datetime
import uuid
from typing import Mapping, Sequence

from snowfall.junction.offers import offers
from snowfall.junction.offers.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis


class NotFoundError(Exception):
    """Raised when an offer aggregate is not found."""


class NoExpiryError(Exception):
    """Raised when an offer bucket list has no expiry."""


def generate_offer_aggregates(
    segment_ids_to_offer_ids: Mapping[str, Sequence[str]],
    expires_at: datetime.datetime,
) -> list[models_pb2.OfferAggregateMapping]:
    offer_ids_to_segment_ids = collections.defaultdict(list)
    for segment_id in segment_ids_to_offer_ids.keys():
        for offer_id in segment_ids_to_offer_ids[segment_id]:
            offer_ids_to_segment_ids[offer_id].append(segment_id)

    return [
        models_pb2.OfferAggregateMapping(
            id=str(uuid.uuid4()),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offer_result_ids=offer_ids,
        )
        for offer_ids in generate_offer_aggregates_recursive(
            segment_ids=list(segment_ids_to_offer_ids),
            segment_ids_to_offer_ids=segment_ids_to_offer_ids,
            offer_ids_to_segment_ids=offer_ids_to_segment_ids,
            fulfilled_segments=frozenset(),
            segment_index=0,
        )
    ]


def generate_offer_aggregates_recursive(
    segment_ids: Sequence[str],
    segment_ids_to_offer_ids: Mapping[str, Sequence[str]],
    offer_ids_to_segment_ids: Mapping[str, Sequence[str]],
    fulfilled_segments: frozenset[str],
    segment_index: int,
) -> list[list[str]]:
    if segment_index >= len(segment_ids):
        return [[]]

    aggregates = []

    for offer_id in segment_ids_to_offer_ids[segment_ids[segment_index]]:
        offer_covers_a_segment_thats_already_covered = any(
            segment_id in fulfilled_segments
            for segment_id in offer_ids_to_segment_ids[offer_id]
        )

        if not offer_covers_a_segment_thats_already_covered:
            current_aggregates = generate_offer_aggregates_recursive(
                segment_ids=segment_ids,
                segment_ids_to_offer_ids=segment_ids_to_offer_ids,
                offer_ids_to_segment_ids=offer_ids_to_segment_ids,
                fulfilled_segments=fulfilled_segments.union(
                    set(offer_ids_to_segment_ids[offer_id]),
                ),
                segment_index=segment_index + 1,
            )
            for aggregate in current_aggregates:
                aggregate.append(offer_id)

            aggregates.extend(current_aggregates)

    return aggregates


class OfferBucketRepository(object):
    def __init__(
        self,
        redis_client: redis.Client[str],
    ):
        self._redis = redis_client

    async def add_offer(self, offer: models_pb2.OfferGroup) -> None:
        for segment in offer.segments:
            key = "{0}:{1}".format(offer.offer_search_id, segment.segment_id)
            bucket = self._redis.list_(key)
            await bucket.push(offer.id)
            await redis.put_expires_at_if_less_than_current(
                self._redis,
                bucket,
                protobuf.protobuf_to_datetime(offer.expires_at),
            )

            bucket_list = self._redis.set_(offer.offer_search_id)
            await bucket_list.add(key)
            await redis.put_expires_at_if_less_than_current(
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

    async def get_bucket_list_expiry(
        self,
        offer_search: models_pb2.OfferSearch,
    ) -> datetime.datetime:
        expires_at = await self._redis.get_expires_at(offer_search.id)

        if not expires_at:
            raise NoExpiryError(
                "Offer bucket list {id} is missing an expiry.".format(
                    id=offer_search.id,
                ),
            )

        return expires_at


class OfferAggregator(object):
    def __init__(
        self,
        offer_searches: offers.OfferSearchRepository,
        offer_buckets: OfferBucketRepository,
        offer_aggregates: offers.OfferAggregateMappingRepository,
    ):
        self._searches = offer_searches
        self._buckets = offer_buckets
        self._aggregates = offer_aggregates

    async def aggregate(self, offer: models_pb2.OfferGroup) -> None:
        offer_search = await self._searches.find_by_id(offer.offer_search_id)

        if not offer_search:
            return

        buckets = await self._buckets.get_offer_buckets(offer.offer_search_id)

        # this overrides the true bucket values for segments that this offer
        # group covers, so that we only generate offer aggregates with this
        # offer group
        for offer_segment in offer.segments:
            buckets[offer_segment.segment_id] = [offer.id]

        await self._buckets.add_offer(offer)

        # check if all segments can be fulfilled by offers gotten so far
        if any(segment.id not in buckets for segment in offer_search.trip.segments):
            return

        expires_at = await self._buckets.get_bucket_list_expiry(offer_search)

        for aggregate in generate_offer_aggregates(buckets, expires_at):
            aggregate.offer_search_id = offer_search.id
            await self._aggregates.insert(aggregate)
