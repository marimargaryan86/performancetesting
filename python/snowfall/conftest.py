from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast

import mongomock_motor
import pytest
from fakeredis import FakeServer
from fakeredis import aioredis as fakeredis
from motor import core
from redis import asyncio as aioredis

pytest.register_assert_rewrite("snowfall.stdlib.integration.starlette.testing")
pytest.register_assert_rewrite("snowfall.stdlib.testing.asserts")


@pytest.fixture()
def mongo_client() -> core.AgnosticClient:
    return cast(core.AgnosticClient, mongomock_motor.AsyncMongoMockClient())


@pytest.fixture()
async def redis_server() -> FakeServer:
    return FakeServer()


@pytest.fixture()
async def redis_client(
    redis_server: FakeServer,
) -> AsyncGenerator[aioredis.Redis[bytes], None]:
    async with fakeredis.FakeRedis(server=redis_server) as client:
        yield client
        await client.connection_pool.disconnect()


@pytest.fixture()
async def decoding_redis_client(
    redis_server: FakeServer,
) -> AsyncGenerator[aioredis.Redis[str], None]:
    async with fakeredis.FakeRedis(
        server=redis_server,
        decode_responses=True,
    ) as client:
        yield client
        await client.connection_pool.disconnect()
