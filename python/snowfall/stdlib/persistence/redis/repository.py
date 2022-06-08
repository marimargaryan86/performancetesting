from __future__ import annotations

import abc
import datetime
import uuid
from typing import Generic, Optional, Type, TypeVar

import pydantic

from snowfall.stdlib.persistence.redis import types as redis


class RedisRecord(pydantic.BaseModel):
    """Record to store in redis as a json object."""


Record = TypeVar("Record", bound=RedisRecord)


class PydanticRepository(Generic[Record]):
    def __init__(
        self,
        client: redis.Client[bytes],
    ):
        self._redis = client

    async def store(
        self,
        record: Record,
        expires_at: Optional[datetime.datetime] = None,
    ) -> str:
        """Store a redis record into the cache and returns a key to access it."""
        key = str(uuid.uuid4())

        await self._redis.put(key, record.json())

        if expires_at is not None:
            await self._redis.put_expires_at(key, expires_at)

        return key

    async def fetch(self, key: str) -> Optional[Record]:
        record_json = await self._redis.get(key)

        if not record_json:
            return None

        return self._record_type.parse_raw(record_json)

    @property
    @abc.abstractmethod
    def _record_type(self) -> Type[Record]:
        raise NotImplementedError()
