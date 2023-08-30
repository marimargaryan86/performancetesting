from __future__ import annotations

import mongomock_motor
import pytest
from fakeredis import FakeServer
from fakeredis import aioredis as fakeredis
from motor import motor_asyncio
from redis import asyncio as aioredis

pytest.register_assert_rewrite("snowfall.stdlib.integration.starlette.testing")
pytest.register_assert_rewrite("snowfall.stdlib.testing.asserts")


@pytest.fixture()
def mongo_client() -> motor_asyncio.AsyncIOMotorClient:
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture()
def redis_client() -> aioredis.Redis[bytes]:
    return fakeredis.FakeRedis(server=FakeServer())


@pytest.fixture()
def decoding_redis_client() -> aioredis.Redis[str]:
    return fakeredis.FakeRedis(server=FakeServer(), decode_responses=True)
