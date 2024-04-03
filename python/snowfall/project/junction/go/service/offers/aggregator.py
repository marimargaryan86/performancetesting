import collections
import datetime
import itertools
from collections.abc import Mapping, Sequence

import prometheus_client
from google.protobuf import timestamp_pb2

from snowfall.project.junction.go.service.offers import offers
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2, models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.v1 import amqp_pb2 as trackable_pb2


class NotFoundError(Exception):
    """Raised when an offer aggregate is not found."""


class NoExpiryError(Exception):
    """Raised when an offer bucket list has no expiry."""


class NoTripSequenceError(Exception):
    """Raised when an offer trip sequence is not found."""


class SkippedOfferError(Exception):
    """Raised when an offer is skipped."""


class IncorrectBucketOfferIdFormatError(Exception):
    """Raised when an offer id is incorrect format (results bucket)."""


def _validate_offer_ids(offer_ids: Sequence[str]) -> None:
    if len(offer_ids) != 2:
        raise IncorrectBucketOfferIdFormatError(
            "Offer {0} is incorrect format.".format(offer_ids),
        )


def _generate_offer_aggregates(
    segment_ids_to_offer_ids: Mapping[str, Sequence[str]],
    expires_at: datetime.datetime,
) -> list[models_pb2.OfferAggregateMapping]:
    offer_ids_to_segment_ids = collections.defaultdict(list)
    for segment_id, offer_ids in segment_ids_to_offer_ids.items():
        for offer_id in offer_ids:
            offer_ids_to_segment_ids[offer_id].append(segment_id)

    return [
        models_pb2.OfferAggregateMapping(
            id=string.uuid(),
            created_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC),
            ),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offer_result_ids=offer_result_ids,
        )
        for offer_result_ids in _generate_offer_aggregates_recursive(
            segment_ids=list(segment_ids_to_offer_ids),
            segment_ids_to_offer_ids=segment_ids_to_offer_ids,
            offer_ids_to_segment_ids=offer_ids_to_segment_ids,
            fulfilled_segments=frozenset(),
            segment_index=0,
        )
    ]


def _generate_offer_aggregates_simple(
    list_offers: Sequence[tuple[str, str]],
    expires_at: datetime.datetime,
) -> list[models_pb2.OfferAggregateMapping]:
    return [
        models_pb2.OfferAggregateMapping(
            id=string.uuid(),
            created_at=protobuf.datetime_to_protobuf(
                datetime.datetime.now(datetime.UTC),
            ),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            offer_result_ids=offer_result_ids,
        )
        for offer_result_ids in list_offers
    ]


def _generate_offer_aggregates_recursive(
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
            current_aggregates = _generate_offer_aggregates_recursive(
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


class OfferBucketRepository:
    INBOUND_BUCKET_NAME = "inbound"  # noqa: WPS115
    OUTBOUND_BUCKET_NAME = "outbound"  # noqa: WPS115
    RESULTS_BUCKET_NAME = "results"  # noqa: WPS115

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
        buckets: dict[str, list[str]] = collections.defaultdict(list)

        async for bucket_name in bucket_list.to_iterable():
            bucket = self._redis.list_(bucket_name)
            bucket_key = bucket_name.split(":")[1]
            buckets[bucket_key] = [
                *buckets[bucket_key],
                *[offer_id async for offer_id in bucket.to_iterable()],
            ]

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

    async def add_offer_to_results_bucket(
        self,
        offer_search_id: str,
        offer_product: tuple[str, str],
        offer_expiry: timestamp_pb2.Timestamp,
    ) -> None:
        product = "{0}:{1}".format(offer_product[0], offer_product[1])

        key = "{0}:{1}".format(
            offer_search_id,
            OfferBucketRepository.RESULTS_BUCKET_NAME,
        )
        bucket = self._redis.list_(key)

        await bucket.push(product)
        await redis.put_expires_at_if_less_than_current(
            self._redis,
            bucket,
            protobuf.protobuf_to_datetime(offer_expiry),
        )

    async def add_offer_outbound(
        self,
        offer_search_id: str,
        offer: models_pb2.OfferGroup,
    ) -> None:
        return await self._add_offer_to_bucket(
            offer_search_id=offer_search_id,
            offer=offer,
            bucket_name=OfferBucketRepository.OUTBOUND_BUCKET_NAME,
        )

    async def add_offer_inbound(
        self,
        offer_search_id: str,
        offer: models_pb2.OfferGroup,
    ) -> None:
        return await self._add_offer_to_bucket(
            offer_search_id=offer_search_id,
            offer=offer,
            bucket_name=OfferBucketRepository.INBOUND_BUCKET_NAME,
        )

    async def get_offer_bucket_results(
        self,
        offer_search_id: str,
    ) -> dict[str, list[tuple[str, str]]]:
        buckets: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)

        key = "{0}:{1}".format(
            offer_search_id,
            OfferBucketRepository.RESULTS_BUCKET_NAME,
        )
        bucket = self._redis.list_(key)
        async for offer_id in bucket.to_iterable():
            offer_ids = offer_id.split(":")
            _validate_offer_ids(offer_ids)
            buckets[OfferBucketRepository.RESULTS_BUCKET_NAME].append((
                offer_ids[0],
                offer_ids[1],
            ))

        return buckets

    async def get_offer_bucket_outbound(
        self,
        offer_search_id: str,
    ) -> list[str]:
        buckets = await self._get_offer_buckets(
            offer_search_id=offer_search_id,
        )
        return buckets[OfferBucketRepository.OUTBOUND_BUCKET_NAME]

    async def get_offer_bucket_inbound(
        self,
        offer_search_id: str,
    ) -> list[str]:
        buckets = await self._get_offer_buckets(
            offer_search_id=offer_search_id,
        )
        return buckets[OfferBucketRepository.INBOUND_BUCKET_NAME]

    async def clear_results_bucket(self, offer_search_id: str) -> None:
        key = "{0}:{1}".format(
            offer_search_id,
            OfferBucketRepository.RESULTS_BUCKET_NAME,
        )
        return await self._redis.delete(key)

    async def _add_offer_to_bucket(
        self,
        offer_search_id: str,
        offer: models_pb2.OfferGroup,
        bucket_name: str,
    ) -> None:
        key = "{0}:{1}".format(offer_search_id, bucket_name)
        bucket = self._redis.list_(key)

        await bucket.push(offer.id)
        await redis.put_expires_at_if_less_than_current(
            self._redis,
            bucket,
            protobuf.protobuf_to_datetime(offer.expires_at),
        )

        bucket_list = self._redis.set_(offer_search_id)
        await bucket_list.add(bucket_name)
        await redis.put_expires_at_if_less_than_current(
            self._redis,
            bucket_list,
            protobuf.protobuf_to_datetime(offer.expires_at),
        )

    async def _get_offer_buckets(self, offer_search_id: str) -> dict[str, list[str]]:
        bucket_list = self._redis.set_(offer_search_id)
        buckets: dict[str, list[str]] = collections.defaultdict(list)

        async for bucket_name in bucket_list.to_iterable():
            key = "{0}:{1}".format(offer_search_id, bucket_name)
            bucket = self._redis.list_(key)
            buckets[bucket_name].extend([
                offer_id async for offer_id in bucket.to_iterable()
            ])

        return buckets


class OfferAggregator:
    _skippable_statuses = (trackable_pb2.Trackable.STATUS_FAILED,)

    _aggregated_total = prometheus_client.Counter(
        "offers_aggregated_total",
        "Total number of offer groups aggregated",
        ["offer_search_status"],
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
        self._logger = stdout.get_logger()

    async def simple_roundtrip_add_offer_to_outbound_bucket(
        self,
        offer: models_pb2.OfferGroup,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        inbound_bucket = await self._buckets.get_offer_bucket_inbound(
            offer_search.id,
        )
        for inbound in inbound_bucket:
            product = (offer.id, inbound)
            await self._buckets.add_offer_to_results_bucket(
                offer_search.id,
                product,
                offer.expires_at,
            )

        await self._buckets.add_offer_outbound(offer_search.id, offer)

    async def simple_roundtrip_add_offer_to_inbound_bucket(
        self,
        offer: models_pb2.OfferGroup,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        outbound_bucket = await self._buckets.get_offer_bucket_outbound(
            offer_search.id,
        )
        for outbound in outbound_bucket:
            product = (outbound, offer.id)
            await self._buckets.add_offer_to_results_bucket(
                offer_search.id,
                product,
                offer.expires_at,
            )

        await self._buckets.add_offer_inbound(offer_search.id, offer)

    async def simple_roundtrip_check_trip_sequence(
        self,
        offer: models_pb2.OfferGroup,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        offer_segment = offer.segments[0]
        trip_sequence = offer_segment.trip_sequence

        if trip_sequence == 1:
            await self.simple_roundtrip_add_offer_to_outbound_bucket(
                offer=offer,
                offer_search=offer_search,
            )
        elif trip_sequence == 2:
            await self.simple_roundtrip_add_offer_to_inbound_bucket(
                offer=offer,
                offer_search=offer_search,
            )
        else:
            raise NoTripSequenceError(
                "Offer search {id} is missing trip sequence.".format(
                    id=offer_search.id,
                ),
            )

    async def simple_roundtrip_aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        _set_sequence_numbers_for_simple_offer(search_result.offer)

        # Assign offer to correct inbound/outbound bucket
        await self.simple_roundtrip_check_trip_sequence(
            offer=search_result.offer,
            offer_search=offer_search,
        )

        results_bucket = await self._buckets.get_offer_bucket_results(offer_search.id)
        offer_results: list[tuple[str, str]] = results_bucket["results"]

        try:
            expires_at = await self._buckets.get_bucket_list_expiry(offer_search)
        except NoExpiryError:
            self._logger.warning(
                "Offer search has expired",
                offer_search_id=offer_search.id,
                provider_company_id=search_result.provider_company_id,
            )
            return

        for aggregate in _generate_offer_aggregates_simple(offer_results, expires_at):
            aggregate.offer_search_id = offer_search.id
            await self._aggregates.insert(aggregate)

        await self._buckets.clear_results_bucket(offer_search.id)

    async def simple_oneway_trip_aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        _set_sequence_numbers_for_simple_offer(search_result.offer)

        buckets = _override_buckets_simple_trip(
            search_result=search_result,
            buckets=await self._buckets.get_offer_buckets(offer_search.id),
        )

        await self._buckets.add_offer(offer_search.id, search_result.offer)

        try:
            expires_at = await self._buckets.get_bucket_list_expiry(offer_search)
        except NoExpiryError:
            self._logger.warning(
                "Offer search has expired",
                offer_search_id=offer_search.id,
                provider_company_id=search_result.provider_company_id,
            )
            return

        for aggregate in _generate_offer_aggregates(buckets, expires_at):
            aggregate.offer_search_id = offer_search.id
            await self._aggregates.insert(aggregate)

    async def simple_trip_aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        if offer_search.simple_trip.HasField("return_departure_at"):
            await self.simple_roundtrip_aggregate(search_result, offer_search)
        else:
            await self.simple_oneway_trip_aggregate(search_result, offer_search)

    async def trip_aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
        offer_search: models_pb2.OfferSearch,
    ) -> None:
        _set_sequence_numbers(offer_search, search_result.offer)
        buckets = _override_buckets(
            search_result=search_result,
            buckets=await self._buckets.get_offer_buckets(offer_search.id),
        )

        await self._buckets.add_offer(offer_search.id, search_result.offer)

        segments = itertools.chain(
            *[trip.segments for trip in offer_search.trip.trips],
        )

        # check if all segments can be fulfilled by offers gotten so far
        if any(segment.id not in buckets for segment in segments):
            return

        try:
            expires_at = await self._buckets.get_bucket_list_expiry(offer_search)
        except NoExpiryError:
            self._logger.warning(
                "Offer search has expired",
                offer_search_id=offer_search.id,
                provider_company_id=search_result.provider_company_id,
            )
            return

        for aggregate in _generate_offer_aggregates(buckets, expires_at):
            aggregate.offer_search_id = offer_search.id
            await self._aggregates.insert(aggregate)

    async def aggregate(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
    ) -> None:
        offer_search = await self._get_offer_search(search_result)
        if offer_search.HasField("simple_trip"):
            await self.simple_trip_aggregate(search_result, offer_search)
        else:
            await self.trip_aggregate(search_result, offer_search)

    async def _get_offer_search(
        self,
        search_result: amqp_pb2.TripOfferSearchResult,
    ) -> models_pb2.OfferSearch:
        offer_search = await self._searches.find_by_id(search_result.offer_search_id)

        if not offer_search:
            raise SkippedOfferError()

        self._aggregated_total.labels(
            offer_search_status=protobuf.enum_value_to_slug(
                trackable_pb2.Trackable.Status.DESCRIPTOR,
                offer_search.status,
            ),
        ).inc()

        if offer_search.status in self._skippable_statuses:
            raise SkippedOfferError()

        if offer_search.status == trackable_pb2.Trackable.STATUS_COMPLETED:
            self._logger.warning(
                "Offer arrived too late",
                offer_search_id=offer_search.id,
                offer_group_id=search_result.offer.id,
                delay_seconds=(
                    datetime.datetime.now(tz=datetime.UTC)
                    - protobuf.protobuf_to_datetime(offer_search.updated_at)
                ).total_seconds(),
            )

        return offer_search


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


def _override_buckets_simple_trip(
    search_result: amqp_pb2.TripOfferSearchResult,
    buckets: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    unqualified_offers: set[str] = set()
    mutable_buckets = dict(buckets)

    for offer_segment in search_result.offer.segments:
        unqualified_offers = {
            *unqualified_offers,
            *mutable_buckets.get(offer_segment.segment_id, set()),
        }
        mutable_buckets[offer_segment.segment_id] = [search_result.offer.id]

    return {idx: list(bucket) for idx, bucket in mutable_buckets.items()}


def _set_sequence_numbers_for_simple_offer(offer: models_pb2.OfferGroup) -> None:
    for segment_seq, segment in enumerate(offer.segments, 1):
        segment.segment_sequence = segment_seq


def _set_sequence_numbers(
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
