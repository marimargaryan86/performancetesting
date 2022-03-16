import datetime

import aioredis
import mongomock_motor
import pytest
from motor import motor_asyncio

from snowfall.junction.offers import aggregator, offers
from snowfall.stdlib.persistence import redis


@pytest.fixture
def mongo_client() -> motor_asyncio.AsyncIOMotorClient:
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture
def offer_bucket_repository(
    decoding_redis_client: aioredis.Redis,
) -> aggregator.OfferBucketRepository:
    return aggregator.OfferBucketRepository(
        redis_client=redis.Client[str](
            redis=decoding_redis_client,
            prefix="offer_bucket",
        ),
    )


@pytest.fixture
def trip_offer_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> offers.TripOfferRepository:
    return offers.TripOfferRepository(collection=mongo_client.offers.trip_offers)


@pytest.fixture
def offer_searches_repository(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> offers.OfferSearchRepository:
    return offers.OfferSearchRepository(
        collection=mongo_client.offers.offer_searches,
        ttl=datetime.timedelta(days=1),
    )


@pytest.fixture
def offer_aggregate_collection(
    mongo_client: motor_asyncio.AsyncIOMotorClient,
) -> motor_asyncio.AsyncIOMotorCollection:
    return mongo_client.offers.offer_aggregates


@pytest.fixture
def offer_aggregate_repository(
    offer_aggregate_collection: motor_asyncio.AsyncIOMotorCollection,
) -> offers.OfferAggregateRepository:
    return offers.OfferAggregateRepository(collection=offer_aggregate_collection)


@pytest.fixture
def offer_aggregator(
    offer_searches_repository: offers.OfferSearchRepository,
    offer_bucket_repository: aggregator.OfferBucketRepository,
    offer_aggregate_repository: offers.OfferAggregateRepository,
) -> aggregator.OfferAggregator:
    return aggregator.OfferAggregator(
        offer_searches=offer_searches_repository,
        offer_buckets=offer_bucket_repository,
        offer_aggregates=offer_aggregate_repository,
    )
