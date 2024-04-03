from __future__ import annotations

import abc
import datetime
from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import v1 as pydantic

from snowfall.stdlib import string
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
        expires_at: datetime.datetime | None = None,
        key: str | None = None,
    ) -> str:
        """Store a redis record into the cache and returns a key to access it."""
        if not key:
            key = string.uuid()

        await self._redis.put(key, record.json(by_alias=True))

        if expires_at is not None:
            await self._redis.put_expires_at(key, expires_at)

        return key

    async def fetch(self, key: str) -> Record | None:
        record_json = await self._redis.get(key)

        if not record_json:
            return None

        return self._record_type.parse_raw(record_json)

    async def mfetch(self, keys: Sequence[str]) -> list[Record | None]:
        record_jsons = await self._redis.mget(keys)

        return [
            (
                self._record_type.parse_raw(record_json)
                if record_json is not None
                else None
            )
            for record_json in record_jsons
        ]

    @property
    @abc.abstractmethod
    def _record_type(self) -> type[Record]:
        raise NotImplementedError()
