from __future__ import annotations

import datetime

import freezegun
import pytest
from redis import asyncio as aioredis

from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.testing import asserts

_PREFIX_PARAMETERS = (("prefix",), [(None,), ("foobar",)])


def _datetimes_are_equal_enough(
    dt1: datetime.datetime | None,
    dt2: datetime.datetime,
) -> None:
    assert dt1 is not None
    # expirations will never be exact to the millisecond, so lets compare if they are
    # at least <1s equal
    assert abs((dt1 - dt2).total_seconds()) < 1


async def _test_expiration(client: redis.Client[bytes], key: object) -> None:
    now = datetime.datetime.now(tz=datetime.UTC)
    next_day = now + datetime.timedelta(days=1)
    next_hour = now + datetime.timedelta(hours=1)

    assert await client.get_expires_at(key) is None

    await client.put_expires_at(key, next_day)
    _datetimes_are_equal_enough(await client.get_expires_at(key), next_day)

    for set_val, get_val in ((next_hour, next_hour), (next_day, next_hour)):
        await redis.put_expires_at_if_less_than_current(client, key, set_val)
        _datetimes_are_equal_enough(await client.get_expires_at(key), get_val)


class TestHash:
    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_delete_get_length_put(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        hash_ = redis.Client(redis_client, prefix=prefix).hash_("foobar")

        await hash_.put("foo", "bar")
        assert await hash_.length() == 1
        assert await hash_.get("foo") == b"bar"
        await hash_.delete("foo")
        assert await hash_.length() == 0

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_expiration(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)
        hash_ = client.hash_("foobar")

        await hash_.put("foo", "bar")

        await _test_expiration(client, hash_)

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_increment(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        hash_ = redis.Client(redis_client, prefix=prefix).hash_("foobar")

        assert await hash_.increment("foo", 1) == 1
        assert await hash_.increment("foo", 10) == 11

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_to_iterable(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        list_ = redis.Client(redis_client, prefix=prefix).list_("foobar")

        await list_.push("foo")
        await list_.push("bar")
        await asserts.assert_iterable(list_.to_iterable(), [b"foo", b"bar"])


class TestList:
    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_length_pop_push(  # noqa: WPS217
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        list_ = redis.Client(redis_client, prefix=prefix).list_("foobar")

        await list_.push("foo")
        assert await list_.length() == 1
        await asserts.assert_iterable(await list_.pop(), [b"foo"])
        assert await list_.length() == 0
        await asserts.assert_iterable(await list_.pop(), [])

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_expiration(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)
        list_ = client.list_("foobar")

        await list_.push("foo")

        await _test_expiration(client, list_)

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_to_iterable(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        list_ = redis.Client(redis_client, prefix=prefix).list_("foobar")

        await list_.push("foo")
        await list_.push("bar")
        await asserts.assert_iterable(list_.to_iterable(), [b"foo", b"bar"])


class TestSet:
    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_add_has_remove(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        set_ = redis.Client(redis_client, prefix=prefix).set_("foobar")

        await set_.add("foo")
        assert await set_.has("foo")
        await set_.remove("foo")
        assert not await set_.has("foo")

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_expiration(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)
        set_ = client.set_("foobar")

        await set_.add("foo")

        await _test_expiration(client, set_)

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_to_iterable(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        set_ = redis.Client(redis_client, prefix=prefix).set_("foobar")

        await set_.add("foo")
        await set_.add("bar")
        await asserts.assert_iterable(set_.to_iterable(), [b"foo", b"bar"])


class TestSortedSet:
    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_add_has_remove(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        sorted_set = redis.Client(redis_client, prefix=prefix).sorted_set("foobar")

        await sorted_set.add("foo", 1)
        assert await sorted_set.get_score("foo")
        await sorted_set.remove("foo")
        assert not await sorted_set.get_score("foo")

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_remove_between_scores(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        sorted_set = redis.Client(redis_client, prefix=prefix).sorted_set("foobar")

        await sorted_set.add("foo", 1)
        await sorted_set.add("bar", 2)
        await sorted_set.add("baz", 3)
        await sorted_set.remove_between_scores(1, 2)
        await asserts.assert_iterable(
            sorted_set.to_iterable(),
            [(b"baz", 3)],
        )

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_expiration(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)
        sorted_set = client.sorted_set("foobar")

        await sorted_set.add("foo", 1)

        await _test_expiration(client, sorted_set)

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_to_iterable(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        sorted_set = redis.Client(redis_client, prefix=prefix).sorted_set("foobar")

        await sorted_set.add("foo", 1)
        await sorted_set.add("bar", 2)
        await asserts.assert_iterable(
            sorted_set.to_iterable(),
            [(b"foo", 1), (b"bar", 2)],
        )


class TestClient:
    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_delete_get_put(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)

        await client.put("foo", "bar")
        assert await client.get("foo") == b"bar"
        await client.delete("foo")
        assert await client.get("foo") is None

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_get_put_with_expiry(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        now = datetime.datetime(year=2023, month=10, day=25, tzinfo=datetime.UTC)
        client = redis.Client(redis_client, prefix=prefix)

        with freezegun.freeze_time(time_to_freeze=now) as frozen_datetime:
            await client.put("foo", "bar", expiry=now + datetime.timedelta(seconds=1))
            assert await client.get("foo") == b"bar"
            frozen_datetime.tick(datetime.timedelta(seconds=2))
            assert await client.get("foo") is None

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_expiration(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)

        await client.put("foo", "bar")
        await _test_expiration(client, "foo")

    @pytest.mark.parametrize(*_PREFIX_PARAMETERS)
    async def test_wildcard_delete(
        self,
        prefix: str | None,
        redis_client: aioredis.Redis[bytes],
    ) -> None:
        client = redis.Client(redis_client, prefix=prefix)

        await client.put("foo.bar", "foobar")
        await client.put("foo.baz", "foobar")

        await asserts.assert_awaitables(
            (client.get("foo.bar"), b"foobar"),
            (client.get("foo.baz"), b"foobar"),
        )

        await client.delete("foo.*")

        await asserts.assert_awaitables(
            (client.get("foo.bar"), None),
            (client.get("foo.baz"), None),
        )

    async def test_prefix(self, redis_client: aioredis.Redis[bytes]) -> None:
        prefixless_client = redis.Client(redis_client)
        foobar_client = redis.Client(redis_client, prefix="foobar")
        bazqux_client = redis.Client(redis_client, prefix="bazqux")

        await prefixless_client.put("foo", "prefixless")
        await foobar_client.put("foo", "foobar")
        await bazqux_client.put("foo", "bazqux")

        assert await prefixless_client.get("foo") == b"prefixless"
        assert await foobar_client.get("foo") == b"foobar"

    async def test_mget(self, redis_client: aioredis.Redis[bytes]) -> None:
        client = redis.Client(redis_client)

        await client.put("foo", "bar")
        await client.put("baz", "qux")

        assert await client.mget(["foo", "baz"]) == [b"bar", b"qux"]
