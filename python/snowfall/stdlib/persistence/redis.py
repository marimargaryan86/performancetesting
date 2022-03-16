from typing import Any, AsyncIterable, Optional

import aioredis


class Hash(object):
    def __init__(self, redis: aioredis.Redis, hash_: str):
        self._hash = hash_
        self._redis = redis

    async def set_(self, hash_key: str, hash_value: Any) -> None:
        await self._redis.hset(self._hash, hash_key, hash_value)

    async def delete(self, hash_key: str) -> None:
        await self._redis.hdel(self._hash, hash_key)

    async def get(self, hash_key: str) -> Optional[bytes]:
        return await self._redis.hget(self._hash, hash_key)

    async def length(self) -> int:
        return await self._redis.hlen(self._hash)

    async def to_iterable(self) -> AsyncIterable[tuple[bytes, bytes]]:
        cursor = 0

        while True:
            cursor, pairs = await self._redis.hscan(name=self._hash, cursor=cursor)

            for pair_key, pair_value in pairs.items():
                yield pair_key, pair_value

            if cursor == 0:
                return


class List(object):
    def __init__(self, redis: aioredis.Redis, list_: str):
        self._list = list_
        self._redis = redis

    async def push(self, list_value: Any) -> None:
        await self._redis.rpush(self._list, list_value)

    async def to_iterable(self, chunk: int = 100) -> AsyncIterable[bytes]:
        length = await self._redis.llen(self._list)
        start = 0

        while start < length:
            stop = start + chunk
            list_values = await self._redis.lrange(self._list, start, stop)

            for list_value in list_values:  # noqa: SIM104
                yield list_value

            start = stop


class Client(object):
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

    async def get(self, name: str) -> Optional[bytes]:
        return await self._redis.get(self._prefix + name)

    def hash_(self, name: str) -> Hash:
        return Hash(self._redis, self._prefix + name)

    def list_(self, name: str) -> List:
        return List(self._redis, self._prefix + name)

    async def set_(self, name: str, raw_value: Any) -> None:
        return await self._redis.set(self._prefix + name, raw_value)
