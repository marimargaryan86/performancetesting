from __future__ import annotations

import datetime

import pytest
from motor import motor_asyncio
from redis import asyncio as aioredis

from snowfall.project.junction.go.service.offers import aggregator, offers
from snowfall.stdlib.persistence.redis import types as redis


@pytest.fixture()
def offer_bucket_repository(
    decoding_redis_client: aioredis.Redis[str],
) -> aggregator.OfferBucketRepository:
    return aggregator.OfferBucketRepository(
        redis_client=redis.Client(
            redis=decoding_redis_client,
            prefix="offer_bucket",
        ),
    )


@pytest.fixture()
def inbound_bucket_repository(
    decoding_redis_client: aioredis.Redis[str],
) -> aggregator.OfferBucketRepository:
    return aggregator.OfferBucketRepository(
        redis_client=redis.Client(
            redis=decoding_redis_client,
            prefix="inbound",
        ),
    )


@pytest.fixture()
def outbound_bucket_repository(
    decoding_redis_client: aioredis.Redis[str],
) -> aggregator.OfferBucketRepository:
    return aggregator.OfferBucketRepository(
        redis_client=redis.Client(
            redis=decoding_redis_client,
            prefix="outbound",
        ),
    )


@pytest.fixture()
def offer_results_bucket_repository(
    decoding_redis_client: aioredis.Redis[str],
) -> aggregator.OfferBucketRepository:
    return aggregator.OfferBucketRepository(
        redis_client=redis.Client(
            redis=decoding_redis_client,
            prefix="results",
        ),
    )


@pytest.fixture()
async def trip_offer_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> offers.TripOfferRepository:
    return offers.TripOfferRepository(collection=mongo_client.test.trip_offers)


@pytest.fixture()
async def offer_options_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> offers.OfferOptionsRepository:
    return offers.OfferOptionsRepository(collection=mongo_client.test.trip_offers)


@pytest.fixture()
async def offer_searches_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> offers.OfferSearchRepository:
    return offers.OfferSearchRepository(
        collection=mongo_client.test.offer_searches,
        ttl=datetime.timedelta(days=1),
    )


@pytest.fixture()
def offer_aggregate_collection(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> motor_asyncio.AsyncIOMotorCollection:
    return mongo_client.test.offer_aggregates


@pytest.fixture()
async def offer_aggregate_repository(
    offer_aggregate_collection: motor_asyncio.AsyncIOMotorCollection,
) -> offers.OfferAggregateMappingRepository:
    return offers.OfferAggregateMappingRepository(collection=offer_aggregate_collection)


@pytest.fixture()
def offer_aggregator(
    offer_searches_repository: offers.OfferSearchRepository,
    offer_bucket_repository: aggregator.OfferBucketRepository,
    offer_aggregate_repository: offers.OfferAggregateMappingRepository,
) -> aggregator.OfferAggregator:
    return aggregator.OfferAggregator(
        offer_searches=offer_searches_repository,
        offer_buckets=offer_bucket_repository,
        offer_aggregates=offer_aggregate_repository,
    )
