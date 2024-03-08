from collections.abc import Mapping, Sequence

from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2,
    models_pb2,
)


def _override_buckets(
    search_task_result: amqp_pb2.SearchTaskResult,
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

    for offer_segment in search_task_result.search_result.offer_segments:
        unqualified_offers = {
            *unqualified_offers,
            *mutable_buckets.get(offer_segment.id, set()),
        }
        mutable_buckets[offer_segment.id] = [
            search_task_result.search_result.id,
        ]

    return {
        idx: [
            search_result_id
            for search_result_id in bucket
            if search_result_id not in unqualified_offers
        ]
        for idx, bucket in mutable_buckets.items()
    }


def _override_buckets_simple_trip(
    search_task_result: amqp_pb2.SearchTaskResult,
    buckets: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    unqualified_offers: set[str] = set()
    mutable_buckets = dict(buckets)

    for offer_segment in search_task_result.search_result.offer_segments:
        unqualified_offers = {
            *unqualified_offers,
            *mutable_buckets.get(offer_segment.id, set()),
        }
        mutable_buckets[offer_segment.id] = [search_task_result.search_result.id]

    return {idx: list(bucket) for idx, bucket in mutable_buckets.items()}


def _set_sequence_numbers_for_simple_offer(
    search_result: models_pb2.SearchResult,
) -> None:
    for segment_seq, segment in enumerate(search_result.offer_segments, 1):
        segment.segment_sequence = segment_seq
