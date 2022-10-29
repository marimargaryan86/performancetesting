import datetime
import random
from typing import Mapping, Sequence

import freezegun
import pytest
from motor import motor_asyncio

from snowfall.project.junction.service.offers import aggregator, offers
from snowfall.project.junction.service.offers.v1alpha import amqp_pb2
from snowfall.project.junction.service.offers.v1alpha import models_pb2 as offer_protos
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.v1alpha import models_pb2

_OFFER_SEARCHES = (
    offer_protos.OfferSearch(
        id="foo",
        trip=offer_protos.TripOfferSearch(
            trips=[
                models_pb2.Trip(
                    id="a",
                    segments=[
                        models_pb2.Segment(
                            id="a",
                        ),
                    ],
                ),
            ],
        ),
    ),
    offer_protos.OfferSearch(
        id="foo",
        trip=offer_protos.TripOfferSearch(
            trips=[
                models_pb2.Trip(
                    id="a",
                    segments=[
                        models_pb2.Segment(
                            id="a",
                        ),
                        models_pb2.Segment(
                            id="b",
                        ),
                    ],
                ),
            ],
        ),
    ),
    offer_protos.OfferSearch(
        id="foo",
        trip=offer_protos.TripOfferSearch(
            trips=[
                models_pb2.Trip(
                    id="a",
                    segments=[
                        models_pb2.Segment(
                            id="a",
                        ),
                    ],
                ),
                models_pb2.Trip(
                    id="b",
                    segments=[
                        models_pb2.Segment(
                            id="b",
                        ),
                        models_pb2.Segment(
                            id="c",
                        ),
                    ],
                ),
            ],
        ),
    ),
)

_OFFER_RESULT_DATE = datetime.datetime(2000, 1, 1)
_OFFER_RESULT_EXPIRY = _OFFER_RESULT_DATE + datetime.timedelta(days=1)
_OFFER_RESULT_EXPIRY_PROTO = protobuf.datetime_to_protobuf(_OFFER_RESULT_EXPIRY)

_OFFER_RESULTS = (
    offer_protos.OfferGroup(
        id="1",
        segments=[
            offer_protos.OfferSegment(
                segment_id="a",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="2",
        segments=[
            offer_protos.OfferSegment(
                segment_id="b",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="3",
        segments=[
            offer_protos.OfferSegment(
                segment_id="b",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="4",
        segments=[
            offer_protos.OfferSegment(
                segment_id="c",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="5",
        segments=[
            offer_protos.OfferSegment(
                segment_id="c",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="6",
        segments=[
            offer_protos.OfferSegment(
                segment_id="a",
            ),
            offer_protos.OfferSegment(
                segment_id="b",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="7",
        segments=[
            offer_protos.OfferSegment(
                segment_id="a",
            ),
            offer_protos.OfferSegment(
                segment_id="b",
            ),
            offer_protos.OfferSegment(
                segment_id="c",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
)


@freezegun.freeze_time(_OFFER_RESULT_DATE)
class TestOfferBuckets(object):
    @pytest.mark.parametrize(
        ["offer_results", "expected"],
        [
            (_OFFER_RESULTS[:1], {"a": ["1"]}),
            (_OFFER_RESULTS[:2], {"a": ["1"], "b": ["2"]}),
            (_OFFER_RESULTS[:3], {"a": ["1"], "b": ["2", "3"]}),
            (
                _OFFER_RESULTS[:5],
                {"a": ["1"], "b": ["2", "3"], "c": ["4", "5"]},
            ),
            (
                _OFFER_RESULTS[:6],
                {"a": ["1", "6"], "b": ["2", "3", "6"], "c": ["4", "5"]},
            ),
            (
                _OFFER_RESULTS[:7],
                {
                    "a": ["1", "6", "7"],
                    "b": ["2", "3", "6", "7"],
                    "c": ["4", "5", "7"],
                },
            ),
        ],
    )
    async def test_offers_are_placed_in_buckets(
        self,
        offer_bucket_repository: aggregator.OfferBucketRepository,
        offer_results: Sequence[offer_protos.OfferGroup],
        expected: Mapping[str, Sequence[str]],
    ) -> None:
        for offer in offer_results:
            await offer_bucket_repository.add_offer("foobar", offer)

        assert (
            await offer_bucket_repository.get_offer_buckets(
                "foobar",
            )
            == expected
        )


@freezegun.freeze_time(_OFFER_RESULT_DATE)
class TestAggregator(object):
    @pytest.mark.parametrize(
        ["offer_search", "offer_results", "expected"],
        [
            (_OFFER_SEARCHES[0], _OFFER_RESULTS[:1], [["1"]]),
            (_OFFER_SEARCHES[1], _OFFER_RESULTS[:2], [["1", "2"]]),
            (
                _OFFER_SEARCHES[1],
                _OFFER_RESULTS[:3],
                [["1", "2"], ["1", "3"]],
            ),
            (
                _OFFER_SEARCHES[2],
                _OFFER_RESULTS[:5],
                [
                    ["1", "2", "4"],
                    ["1", "3", "4"],
                    ["1", "2", "5"],
                    ["1", "3", "5"],
                ],
            ),
            (
                _OFFER_SEARCHES[2],
                _OFFER_RESULTS[:6],
                [
                    ["1", "2", "4"],
                    ["1", "3", "4"],
                    ["1", "2", "5"],
                    ["1", "3", "5"],
                    ["6", "4"],
                    ["6", "5"],
                ],
            ),
            (
                _OFFER_SEARCHES[2],
                _OFFER_RESULTS[:7],
                [
                    ["1", "2", "4"],
                    ["1", "3", "4"],
                    ["1", "2", "5"],
                    ["1", "3", "5"],
                    ["6", "4"],
                    ["6", "5"],
                    ["7"],
                ],
            ),
        ],
    )
    async def test_offers_generate_expected_aggregates(
        self,
        offer_searches_repository: offers.OfferSearchRepository,
        offer_aggregator: aggregator.OfferAggregator,
        offer_aggregate_collection: motor_asyncio.AsyncIOMotorCollection,
        offer_search: offer_protos.OfferSearch,
        offer_results: Sequence[offer_protos.OfferGroup],
        expected: Sequence[Sequence[str]],
    ) -> None:
        await offer_searches_repository.insert(offer_search)

        for offer_result in random.sample(list(offer_results), len(offer_results)):
            await offer_aggregator.aggregate(
                amqp_pb2.TripOfferSearchResult(
                    offer_search_id=offer_search.id,
                    offer=offer_result,
                ),
            )

        expected_sorted = [sorted(aggregate) for aggregate in expected]
        async for aggregate in offer_aggregate_collection.find():
            assert sorted(aggregate["offer_result_ids"]) in expected_sorted
            assert aggregate["expires_at"] == _OFFER_RESULT_EXPIRY

        assert await offer_aggregate_collection.count_documents({}) == len(expected)
