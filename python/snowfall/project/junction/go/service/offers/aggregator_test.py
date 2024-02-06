import datetime
import random
from collections.abc import Mapping, Sequence

import freezegun
import pytest
from motor import core

from snowfall.project.junction.go.service.offers import aggregator, offers
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2
from snowfall.project.junction.go.service.offers.v1 import models_pb2 as offer_protos
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf

_OFFER_RESULT_DATE = datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)
_OFFER_RESULT_EXPIRY = _OFFER_RESULT_DATE + datetime.timedelta(days=1)
_OFFER_RESULT_EXPIRY_PROTO = protobuf.datetime_to_protobuf(_OFFER_RESULT_EXPIRY)

_OFFER_RESULT_RETURN_DATE = datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)


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

_SIMPLE_OFFER_SEARCHES = (
    offer_protos.OfferSearch(
        id="foo",
        simple_trip=offer_protos.SimpleTripOfferSearch(
            departure_at=protobuf.datetime_to_protobuf(_OFFER_RESULT_DATE),
            return_departure_at=protobuf.datetime_to_protobuf(
                _OFFER_RESULT_RETURN_DATE,
            ),
        ),
    ),
)

_SIMPLE_OFFER_GROUP_RESULTS = (
    offer_protos.OfferGroup(
        id="1",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=1,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="2",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=2,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="3",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=2,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="4",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=1,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="5",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=2,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
    offer_protos.OfferGroup(
        id="6",
        segments=[
            offer_protos.OfferSegment(
                trip_sequence=1,
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY_PROTO,
    ),
)


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
        ("offer_results", "expected"),
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

    @pytest.mark.parametrize(
        ("offer_results", "expected"),
        [
            (_SIMPLE_OFFER_GROUP_RESULTS[:1], ["1"]),
            (_SIMPLE_OFFER_GROUP_RESULTS[:2], ["1", "2"]),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[:5],
                ["1", "2", "3", "4", "5"],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[:],
                ["1", "2", "3", "4", "5", "6"],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[-5:],
                ["2", "3", "4", "5", "6"],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[-2:],
                ["5", "6"],
            ),
        ],
    )
    async def test_offers_are_placed_in_buckets_simple_trip(
        self,
        inbound_bucket_repository: aggregator.OfferBucketRepository,
        outbound_bucket_repository: aggregator.OfferBucketRepository,
        offer_results: Sequence[offer_protos.OfferGroup],
        expected: Sequence[str],
    ) -> None:
        offer_search_id = "foobar"
        for offer in offer_results:
            await inbound_bucket_repository.add_offer_inbound(offer_search_id, offer)
            await outbound_bucket_repository.add_offer_outbound(offer_search_id, offer)

        inbound = await inbound_bucket_repository.get_offer_bucket_inbound(
            offer_search_id,
        )
        outbound = await outbound_bucket_repository.get_offer_bucket_outbound(
            offer_search_id,
        )

        assert inbound == expected
        assert outbound == expected

    @pytest.mark.parametrize(
        ("offer_results", "expected"),
        [
            (_SIMPLE_OFFER_GROUP_RESULTS[:1], [("1", "1")]),
            (_SIMPLE_OFFER_GROUP_RESULTS[:2], [("1", "1"), ("2", "2")]),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[:5],
                [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[:],
                [
                    ("1", "1"),
                    ("2", "2"),
                    ("3", "3"),
                    ("4", "4"),
                    ("5", "5"),
                    ("6", "6"),
                ],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[-5:],
                [("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6")],
            ),
            (
                _SIMPLE_OFFER_GROUP_RESULTS[-2:],
                [("5", "5"), ("6", "6")],
            ),
        ],
    )
    async def test_offers_are_placed_in_results_buckets_simple_trip(
        self,
        offer_results_bucket_repository: aggregator.OfferBucketRepository,
        offer_results: Sequence[offer_protos.OfferGroup],
        expected: Sequence[tuple[str, str]],
    ) -> None:
        offer_search_id = "foobar"
        for offer in offer_results:
            offer_product = (offer.id, offer.id)
            # Pass in a tuple 'offer_product', consists of ('outbound_offer', 'inbound_offer')
            await offer_results_bucket_repository.add_offer_to_results_bucket(
                offer_search_id,
                offer_product,
                _OFFER_RESULT_EXPIRY_PROTO,
            )
            # add_offer_to_results_bucket() will split the tuple and push a formatted string to bucket
            # The formatted string is the 2 ids separated with a colon. i.e. "2:3"

        offers_from_bucket = (
            await offer_results_bucket_repository.get_offer_bucket_results(
                offer_search_id,
            )
        )

        assert offers_from_bucket["results"] == expected


@freezegun.freeze_time(_OFFER_RESULT_DATE)
class TestAggregator(object):
    @pytest.mark.parametrize(
        ("offer_search", "offer_results", "expected"),
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
        offer_aggregate_collection: core.AgnosticCollection,
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
            assert (
                aggregate["expires_at"].replace(tzinfo=datetime.UTC)
                == _OFFER_RESULT_EXPIRY
            )

        assert await offer_aggregate_collection.count_documents({}) == len(expected)


@freezegun.freeze_time(_OFFER_RESULT_DATE)
class TestSimpleSearchAggregator(object):
    @pytest.mark.parametrize(
        ("offer_search", "offer_results", "expected"),
        [
            (_SIMPLE_OFFER_SEARCHES[0], _SIMPLE_OFFER_GROUP_RESULTS[:2], [["1", "2"]]),
            (
                _SIMPLE_OFFER_SEARCHES[0],
                _SIMPLE_OFFER_GROUP_RESULTS[:4],
                [["1", "2"], ["1", "3"], ["4", "2"], ["4", "3"]],
            ),
            (
                _SIMPLE_OFFER_SEARCHES[0],
                _SIMPLE_OFFER_GROUP_RESULTS,
                [
                    ["1", "2"],
                    ["1", "5"],
                    ["1", "3"],
                    ["4", "2"],
                    ["4", "5"],
                    ["4", "3"],
                    ["6", "2"],
                    ["6", "5"],
                    ["6", "3"],
                ],
            ),
        ],
    )
    async def test_offers_generate_expected_simple_trip_aggregate(
        self,
        offer_searches_repository: offers.OfferSearchRepository,
        offer_aggregator: aggregator.OfferAggregator,
        offer_aggregate_collection: core.AgnosticCollection,
        offer_search: offer_protos.OfferSearch,
        offer_results: Sequence[offer_protos.OfferGroup],
        expected: Sequence[Sequence[str]],
    ) -> None:
        await offer_searches_repository.insert(offer_search)

        for offer_result in random.sample(list(offer_results), len(offer_results)):
            await offer_aggregator.simple_trip_aggregate(
                search_result=amqp_pb2.TripOfferSearchResult(
                    offer_search_id=offer_search.id,
                    offer=offer_result,
                ),
                offer_search=offer_search,
            )

        all_aggregated = []
        async for aggregate in offer_aggregate_collection.find():
            all_aggregated.append(aggregate["offer_result_ids"])
            assert aggregate["offer_result_ids"] in expected
            assert (
                aggregate["expires_at"].replace(tzinfo=datetime.UTC)
                == _OFFER_RESULT_EXPIRY
            )
        assert len(all_aggregated) == len(expected)

        aggregated_set = {tuple(item) for item in all_aggregated}
        expected_set = {tuple(item) for item in expected}
        assert aggregated_set == expected_set, "Aggregates don't have expected offers"
