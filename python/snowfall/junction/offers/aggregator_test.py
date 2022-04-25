import datetime
from typing import Mapping, Sequence

import pytest
from motor import motor_asyncio

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.offers import aggregator, offers
from snowfall.junction.offers.v1alpha import offers_pb2
from snowfall.junction.providers.v1alpha import offers_pb2 as provider_offers_pb2
from snowfall.stdlib.format import protobuf

_OFFER_SEARCHES = (
    offers_pb2.OfferSearch(
        id="foo",
        trip=offers_pb2.TripOfferSearch(
            segments=[
                models_pb2.Segment(
                    id="a",
                ),
            ],
        ),
    ),
    offers_pb2.OfferSearch(
        id="foo",
        trip=offers_pb2.TripOfferSearch(
            segments=[
                models_pb2.Segment(
                    id="a",
                ),
                models_pb2.Segment(
                    id="b",
                ),
            ],
        ),
    ),
    offers_pb2.OfferSearch(
        id="foo",
        trip=offers_pb2.TripOfferSearch(
            segments=[
                models_pb2.Segment(
                    id="a",
                ),
                models_pb2.Segment(
                    id="b",
                ),
                models_pb2.Segment(
                    id="c",
                ),
            ],
        ),
    ),
)

_OFFER_RESULT_EXPIRY = protobuf.datetime_to_protobuf(
    datetime.datetime.now() + datetime.timedelta(days=1),
)

_OFFER_RESULTS = (
    provider_offers_pb2.GroupedOffer(
        id="1",
        offer_search_id="foo",
        segments=[
            provider_offers_pb2.Segment(
                id="a",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY,
    ),
    provider_offers_pb2.GroupedOffer(
        id="2",
        offer_search_id="foo",
        segments=[
            provider_offers_pb2.Segment(
                id="b",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY,
    ),
    provider_offers_pb2.GroupedOffer(
        id="3",
        offer_search_id="foo",
        segments=[
            provider_offers_pb2.Segment(
                id="b",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY,
    ),
    provider_offers_pb2.GroupedOffer(
        id="4",
        offer_search_id="foo",
        segments=[
            provider_offers_pb2.Segment(
                id="c",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY,
    ),
    provider_offers_pb2.GroupedOffer(
        id="5",
        offer_search_id="foo",
        segments=[
            provider_offers_pb2.Segment(
                id="c",
            ),
        ],
        expires_at=_OFFER_RESULT_EXPIRY,
    ),
)


@pytest.mark.asyncio
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
        ],
    )
    async def test_offers_are_placed_in_buckets(
        self,
        offer_bucket_repository: aggregator.OfferBucketRepository,
        offer_results: Sequence[provider_offers_pb2.GroupedOffer],
        expected: Mapping[str, Sequence[str]],
    ) -> None:
        for offer in offer_results:
            await offer_bucket_repository.add_offer(offer)

        assert (
            await offer_bucket_repository.get_offer_buckets(
                offer_results[0].offer_search_id,
            )
            == expected
        )


@pytest.mark.asyncio
class TestAggregator(object):
    @pytest.mark.parametrize(
        ["offer_search", "offer_results", "expected"],
        [
            (_OFFER_SEARCHES[0], _OFFER_RESULTS[:1], 1),
            (_OFFER_SEARCHES[1], _OFFER_RESULTS[:2], 1),
            (_OFFER_SEARCHES[1], _OFFER_RESULTS[:3], 2),
            (_OFFER_SEARCHES[2], _OFFER_RESULTS[:5], 4),
        ],
    )
    async def test_offers_generate_expected_number_of_aggregates(
        self,
        offer_searches_repository: offers.OfferSearchRepository,
        offer_aggregator: aggregator.OfferAggregator,
        offer_aggregate_collection: motor_asyncio.AsyncIOMotorCollection,
        offer_search: offers_pb2.OfferSearch,
        offer_results: Sequence[provider_offers_pb2.GroupedOffer],
        expected: int,
    ) -> None:
        await offer_searches_repository.insert(offer_search)

        for offer_result in offer_results:
            await offer_aggregator.aggregate(offer_result)

        assert await offer_aggregate_collection.count_documents({}) == expected

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
        ],
    )
    async def test_offers_generate_expected_aggregates(
        self,
        offer_searches_repository: offers.OfferSearchRepository,
        offer_aggregator: aggregator.OfferAggregator,
        offer_aggregate_collection: motor_asyncio.AsyncIOMotorCollection,
        offer_search: offers_pb2.OfferSearch,
        offer_results: Sequence[provider_offers_pb2.GroupedOffer],
        expected: Sequence[Sequence[str]],
    ) -> None:
        await offer_searches_repository.insert(offer_search)
        for offer_result in offer_results:
            await offer_aggregator.aggregate(offer_result)

        async for aggregate in offer_aggregate_collection.find():
            assert aggregate["offer_result_ids"] in expected
