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
    unqualified_searches: set[str] = set()
    mutable_buckets = dict(buckets)

    for result_detail in search_task_result.search_result.result_details:
        unqualified_searches = {
            *unqualified_searches,
            *mutable_buckets.get(result_detail.id, set()),
        }
        mutable_buckets[result_detail.id] = [
            search_task_result.search_result.id,
        ]

    return {
        idx: [
            search_result_id
            for search_result_id in bucket
            if search_result_id not in unqualified_searches
        ]
        for idx, bucket in mutable_buckets.items()
    }


def _override_buckets_simple_trip(
    search_task_result: amqp_pb2.SearchTaskResult,
    buckets: Mapping[str, Sequence[str]],
) -> dict[str, list[str]]:
    unqualified_search_results: set[str] = set()
    mutable_buckets = dict(buckets)

    for result_detail in search_task_result.search_result.result_details:
        unqualified_search_results = {
            *unqualified_search_results,
            *mutable_buckets.get(result_detail.id, set()),
        }
        mutable_buckets[result_detail.id] = [search_task_result.search_result.id]

    return {idx: list(bucket) for idx, bucket in mutable_buckets.items()}


def _set_sequence_numbers_for_search(
    search_result: models_pb2.SearchResult,
) -> None:
    for segment_seq, segment in enumerate(search_result.result_details, 1):
        segment.segment_sequence = segment_seq
