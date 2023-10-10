from __future__ import annotations

import datetime

from redis import asyncio as aioredis

from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.persistence.redis.repository import (
    PydanticRepository as RedisRepository,
)
from snowfall.stdlib.persistence.redis.repository import RedisRecord


class FooRecord(RedisRecord):
    test_id: str
    created_at: datetime.datetime


class FooRepository(RedisRepository[FooRecord]):
    """Test repository."""

    _record_type: type[FooRecord] = FooRecord


async def test_record_can_be_created(
    redis_client: aioredis.Redis[bytes],
) -> None:
    repository = FooRepository(
        client=redis.Client(redis_client),
    )
    record = FooRecord(
        test_id="test",
        created_at=datetime.datetime.now(tz=datetime.UTC),
    )
    key = await repository.store(record)
    stored_record = await repository.fetch(key)
    assert record == stored_record


async def test_record_can_be_created_with_custom_id(
    redis_client: aioredis.Redis[bytes],
) -> None:
    repository = FooRepository(
        client=redis.Client(redis_client),
    )
    record = FooRecord(
        test_id="test",
        created_at=datetime.datetime.now(tz=datetime.UTC),
    )
    key = "test-key"
    await repository.store(record, key=key)
    stored_record = await repository.fetch(key)
    assert record == stored_record
