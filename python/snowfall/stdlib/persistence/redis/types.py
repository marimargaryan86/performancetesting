from __future__ import annotations

import datetime
from typing import AnyStr, AsyncIterable, Generic

from redis.asyncio import Redis, lock


class Hash(Generic[AnyStr]):  # noqa: WPS214
    def __init__(self, redis: Redis[AnyStr], name: str):
        self._name = name
        self._redis: Redis[AnyStr] = redis

    def __str__(self) -> str:
        return self._name

    async def increment(self, hash_key: str, amount: int = 1) -> int:
        return await self._redis.hincrby(self._name, hash_key, amount)

    async def put(
        self,
        hash_key: str,
        hash_value: bytes | float | int | str,
    ) -> None:
        await self._redis.hset(self._name, hash_key, hash_value)

    async def delete(self, hash_key: str) -> None:
        await self._redis.hdel(self._name, hash_key)

    async def get(self, hash_key: str) -> AnyStr | None:
        return await self._redis.hget(self._name, hash_key)

    async def length(self) -> int:
        return await self._redis.hlen(self._name)

    async def to_iterable(self) -> AsyncIterable[tuple[AnyStr, AnyStr]]:
        cursor = 0

        while True:
            cursor, pairs = await self._redis.hscan(name=self._name, cursor=cursor)

            for pair_key, pair_value in pairs.items():
                yield pair_key, pair_value

            if cursor == 0:
                return


class List(Generic[AnyStr]):
    def __init__(self, redis: Redis[AnyStr], name: str):
        self._name = name
        self._redis: Redis[AnyStr] = redis

    def __str__(self) -> str:
        return self._name

    async def push(self, list_value: bytes | float | int | str) -> None:
        await self._redis.rpush(self._name, list_value)

    async def to_iterable(self, chunk: int = 100) -> AsyncIterable[AnyStr]:
        length = await self._redis.llen(self._name)
        start = 0

        while start < length:
            stop = start + chunk
            list_values = await self._redis.lrange(self._name, start, stop)

            for list_value in list_values:
                yield list_value

            start = stop


class Set(Generic[AnyStr]):
    def __init__(self, redis: Redis[AnyStr], name: str):
        self._name = name
        self._redis: Redis[AnyStr] = redis

    def __str__(self) -> str:
        return self._name

    async def add(self, set_value: bytes | float | int | str) -> None:
        await self._redis.sadd(self._name, set_value)

    async def to_iterable(self) -> AsyncIterable[AnyStr]:
        cursor = 0

        while True:
            cursor, keys = await self._redis.sscan(name=self._name, cursor=cursor)

            for key in keys:
                yield key

            if cursor == 0:
                return


class Client(Generic[AnyStr]):  # noqa: WPS214
    def __init__(self, redis: Redis[AnyStr], prefix: str = ""):
        self._prefix = "{0}:".format(prefix) if prefix else ""
        self._redis: Redis[AnyStr] = redis

    async def delete(self, key: str) -> None:
        if "*" not in key:
            await self._redis.delete(self._prefix + key)
            return

        cursor = 0

        while True:
            cursor, keys_list = await self._redis.scan(
                cursor=cursor,
                match=self._prefix + key,
            )

            if keys_list:
                await self._redis.delete(*keys_list)

            if cursor == 0:
                break

    async def get(self, name: str) -> AnyStr | None:
        return await self._redis.get(self._prefix + name)

    def hash_(self, name: str) -> Hash[AnyStr]:
        return Hash(self._redis, self._prefix + name)

    def list_(self, name: str) -> List[AnyStr]:
        return List(self._redis, self._prefix + name)

    def set_(self, name: str) -> Set[AnyStr]:
        return Set(self._redis, self._prefix + name)

    def lock(  # noqa: WPS211
        self,
        name: str,
        timeout: float | None = None,
        sleep: float = 0.1,
        blocking: bool = True,
        blocking_timeout: float | None = None,
        thread_local: bool = True,
    ) -> lock.Lock:
        return lock.Lock(
            redis=self._redis,
            name=self._prefix + name,
            timeout=timeout,
            sleep=sleep,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
            thread_local=thread_local,
        )

    async def put(self, name: str, raw_value: bytes | float | int | str) -> None:
        await self._redis.set(self._prefix + name, raw_value)

    async def put_expires_at(
        self,
        name: object,
        expiry: datetime.datetime | datetime.timedelta,
    ) -> None:
        if isinstance(expiry, datetime.datetime):
            expiry = expiry - datetime.datetime.now(tz=datetime.timezone.utc)

        await self._redis.expire(self._prefix_name(name), expiry)

    async def get_expires_at(self, name: object) -> datetime.datetime | None:
        expiry = await self._redis.pttl(self._prefix_name(name))

        # `pttl` should return `int`, but we have seen `None` and `str`
        if not isinstance(expiry, int) or expiry < 0:  # type: ignore[redundant-expr]
            return None

        return datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(milliseconds=expiry)

    def _prefix_name(self, name: object) -> str:
        if isinstance(name, str):
            return self._prefix + name

        return str(name)


async def put_expires_at_if_less_than_current(
    redis_client: Client[AnyStr],
    name: object,
    expiry: datetime.datetime | datetime.timedelta,
) -> None:
    if isinstance(expiry, datetime.timedelta):
        expiry = datetime.datetime.now(tz=datetime.timezone.utc) + expiry

    expiry_at = await redis_client.get_expires_at(name)

    if expiry_at and expiry > expiry_at:
        return

    await redis_client.put_expires_at(name, expiry)
