import collections
import datetime
import itertools
from typing import Mapping, Sequence

from snowfall.project.junction.service.offers import offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2, models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1alpha import amqp_pb2 as trackable_pb2


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
            id=string.uuid(),
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


def generate_offer_aggregates_recursive(  # noqa: WPS210
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
                fulfilled_segments=frozenset(
                    (
                        *fulfilled_segments,
                        *offer_ids_to_segment_ids[offer_id],
                    ),
                ),
                segment_index=next(
                    (
                        segment_idx
                        for segment_idx, segment_id in enumerate(segment_ids)
                        if segment_id
                        not in {
                            *fulfilled_segments,
                            *offer_ids_to_segment_ids[offer_id],
                        }
                    ),
                    len(segment_ids),
                ),
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

    async def add_offer(
        self,
        offer_search_id: str,
        offer: models_pb2.OfferGroup,
    ) -> None:
        for segment in offer.segments:
            key = "{0}:{1}".format(offer_search_id, segment.segment_id)
            bucket = self._redis.list_(key)
            await bucket.push(offer.id)
            await redis.put_expires_at_if_less_than_current(
                self._redis,
                bucket,
                protobuf.protobuf_to_datetime(offer.expires_at),
            )

            bucket_list = self._redis.set_(offer_search_id)
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
    _skippable_statuses = (
        trackable_pb2.Trackable.STATUS_FAILED,
        trackable_pb2.Trackable.STATUS_COMPLETED,
    )

    def __init__(
        self,
        offer_searches: offers.OfferSearchRepository,
        offer_buckets: OfferBucketRepository,
        offer_aggregates: offers.OfferAggregateMappingRepository,
    ):
        self._searches = offer_searches
        self._buckets = offer_buckets
        self._aggregates = offer_aggregates

    async def aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
    ) -> None:
        offer_search = await self._searches.find_by_id(search_result.offer_search_id)

        if not offer_search or offer_search.status in self._skippable_statuses:
            return

        _set_sequence_numbers(offer_search, search_result.offer)

        buckets = _override_buckets(
            search_result,
            await self._buckets.get_offer_buckets(offer_search.id),
        )

        await self._buckets.add_offer(offer_search.id, search_result.offer)

        segments = itertools.chain(*[trip.segments for trip in offer_search.trip.trips])

        # check if all segments can be fulfilled by offers gotten so far
        if any(segment.id not in buckets for segment in segments):
            return

        expires_at = await self._buckets.get_bucket_list_expiry(offer_search)

        for aggregate in generate_offer_aggregates(buckets, expires_at):
            aggregate.offer_search_id = offer_search.id
            await self._aggregates.insert(aggregate)


def _override_buckets(
    search_result: amqp_pb2.TripOfferSearchResult,
    buckets: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    # this overrides the true bucket values for segments that this offer
    # group covers, so that we only generate offer aggregates with this
    # offer group
    #
    # we also need to mark all offers we override as unqualified, so we
    # can remove multi-segment offers from other buckets they're in, else
    # we'll end up with partial offers
    unqualified_offers: set[str] = set()
    mutable_buckets = dict(buckets)

    for offer_segment in search_result.offer.segments:
        unqualified_offers = {
            *unqualified_offers,
            *mutable_buckets.get(offer_segment.segment_id, set()),
        }

        mutable_buckets[offer_segment.segment_id] = [search_result.offer.id]

    return {
        idx: [offer_id for offer_id in bucket if offer_id not in unqualified_offers]
        for idx, bucket in mutable_buckets.items()
    }


def _set_sequence_numbers(  # noqa: WPS210
    offer_search: models_pb2.OfferSearch,
    offer: models_pb2.OfferGroup,
) -> None:
    sequence_mapping: dict[str, tuple[int, int]] = {}

    for trip_idx, trip in enumerate(offer_search.trip.trips):
        for segment_idx, trip_segment in enumerate(trip.segments):
            sequence_mapping[trip_segment.id] = (trip_idx + 1, segment_idx + 1)

    for segment in offer.segments:
        trip_sequence, segment_sequence = sequence_mapping[segment.segment_id]
        segment.trip_sequence = trip_sequence
        segment.segment_sequence = segment_sequence
