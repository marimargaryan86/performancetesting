import datetime
from typing import Any, AnyStr, AsyncIterable, Generic, Optional

import aioredis


class Hash(Generic[AnyStr]):
    def __init__(self, redis: aioredis.Redis, name: str):
        self._name = name
        self._redis = redis

    def __str__(self) -> str:
        return self._name

    async def put(self, hash_key: str, hash_value: Any) -> None:
        await self._redis.hset(self._name, hash_key, hash_value)

    async def delete(self, hash_key: str) -> None:
        await self._redis.hdel(self._name, hash_key)

    async def get(self, hash_key: str) -> Optional[AnyStr]:
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
    def __init__(self, redis: aioredis.Redis, name: str):
        self._name = name
        self._redis = redis

    def __str__(self) -> str:
        return self._name

    async def push(self, list_value: Any) -> None:
        await self._redis.rpush(self._name, list_value)

    async def to_iterable(self, chunk: int = 100) -> AsyncIterable[AnyStr]:
        length = await self._redis.llen(self._name)
        start = 0

        while start < length:
            stop = start + chunk
            list_values = await self._redis.lrange(self._name, start, stop)

            for list_value in list_values:  # noqa: SIM104
                yield list_value

            start = stop


class Set(Generic[AnyStr]):
    def __init__(self, redis: aioredis.Redis, name: str):
        self._name = name
        self._redis = redis

    def __str__(self) -> str:
        return self._name

    async def add(self, name: str) -> None:
        await self._redis.sadd(self._name, name)

    async def to_iterable(self) -> AsyncIterable[AnyStr]:
        cursor = 0

        while True:
            cursor, keys = await self._redis.sscan(name=self._name, cursor=cursor)

            for key in keys:  # noqa: SIM104
                yield key

            if cursor == 0:
                return


class Client(Generic[AnyStr]):  # noqa: WPS214
    def __init__(self, redis: aioredis.Redis, prefix: str = ""):
        self._prefix = "{0}:".format(prefix) if prefix else ""
        self._redis = redis

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

    async def get(self, name: str) -> Optional[AnyStr]:
        return await self._redis.get(self._prefix + name)

    def hash_(self, name: str) -> Hash[AnyStr]:
        return Hash[AnyStr](self._redis, self._prefix + name)

    def list_(self, name: str) -> List[AnyStr]:
        return List[AnyStr](self._redis, self._prefix + name)

    def set_(self, name: str) -> Set[AnyStr]:
        return Set[AnyStr](self._redis, self._prefix + name)

    async def put(self, name: str, raw_value: Any) -> None:
        return await self._redis.set(self._prefix + name, raw_value)

    async def put_expires_at(self, name: object, expiry: datetime.datetime) -> None:
        expires_in = expiry - datetime.datetime.now(tz=datetime.timezone.utc)
        await self._redis.expire(self._prefix_name(name), expires_in)

    async def get_expires_at(self, name: object) -> Optional[datetime.datetime]:
        expiry = await self._redis.pttl(self._prefix_name(name))

        if expiry < 0:
            return None

        return datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(milliseconds=expiry)

    def _prefix_name(self, name: object) -> str:
        if isinstance(name, str):
            return self._prefix + name

        return str(name)


async def put_expires_at_if_less_than_current(
    client: Client[AnyStr],
    name: object,
    expiry: datetime.datetime,
) -> None:
    expiry_at = await client.get_expires_at(name)

    if expiry_at and expiry_at > expiry:
        return

    await client.put_expires_at(name, expiry)
