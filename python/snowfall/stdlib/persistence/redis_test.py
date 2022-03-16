import asyncio

import aioredis
import pytest

from snowfall.stdlib.persistence import redis
from snowfall.stdlib.testing import asserts


@pytest.mark.asyncio
class TestClient(object):
    async def test_set_get_delete(self) -> None:
        await self._client.set_("foobar", "bazqux")

        assert await self._client.get("foobar") == b"bazqux"

        await self._client.delete("foobar")

        assert await self._client.get("foobar") is None

    async def test_wildcard_delete(self) -> None:
        await asyncio.gather(
            self._client.set_("foo.bar", "foobar"),
            self._client.set_("foo.baz", "foobar"),
            self._client.set_("bar.baz", "foobar"),
        )

        await self._client.delete("foo.*")

        await asserts.assert_awaitables(
            (self._client.get("foo.bar"), None),
            (self._client.get("foo.baz"), None),
            (self._client.get("bar.baz"), b"foobar"),
        )

    async def test_hash(self) -> None:
        hash_ = self._client.hash_("foobar")

        await asyncio.gather(
            hash_.set_("foobar", "foobar"),
            hash_.set_("bazqux", "bazqux"),
        )

        await asserts.assert_iterable(
            hash_.to_iterable(),
            [
                (b"bazqux", b"bazqux"),
                (b"foobar", b"foobar"),
            ],
        )

        await asserts.assert_awaitables(
            (hash_.length(), 2),
            (hash_.get("foobar"), b"foobar"),
        )

        await hash_.delete("foobar")

        await asserts.assert_awaitables(
            (hash_.length(), 1),
            (hash_.get("foobar"), None),
            (hash_.get("bazqux"), b"bazqux"),
        )

    async def test_list(self) -> None:
        list_ = self._client.list_("foobar")

        await asyncio.gather(
            list_.push("foobar"),
            list_.push("bazqux"),
        )

        await asserts.assert_iterable(
            list_.to_iterable(),
            [
                b"foobar",
                b"bazqux",
            ],
        )

    @pytest.fixture(autouse=True)
    def _setup(self, redis_client: aioredis.Redis) -> None:
        self._client = redis.Client(redis_client)


@pytest.mark.asyncio
class TestPrefixClient(object):
    async def test_set_get_delete(self, redis_client: aioredis.Redis) -> None:
        await asyncio.gather(
            self._foo_client.set_("foobar", "foobar"),
            self._bar_client.set_("foobar", "bazqux"),
        )

        await asserts.assert_awaitables(
            (self._foo_client.get("foobar"), b"foobar"),
            (self._bar_client.get("foobar"), b"bazqux"),
        )

        await self._bar_client.delete("foobar")

        await asserts.assert_awaitables(
            (self._foo_client.get("foobar"), b"foobar"),
            (self._bar_client.get("foobar"), None),
        )

    async def test_wildcard_delete(self, redis_client: aioredis.Redis) -> None:
        await asyncio.gather(
            self._foo_client.set_("foo.bar", "foobar"),
            self._foo_client.set_("foo.baz", "foobar"),
            self._bar_client.set_("foo.bar", "bazqux"),
            self._bar_client.set_("foo.baz", "bazqux"),
        )

        await asserts.assert_awaitables(
            (self._foo_client.get("foo.bar"), b"foobar"),
            (self._foo_client.get("foo.baz"), b"foobar"),
            (self._bar_client.get("foo.bar"), b"bazqux"),
            (self._bar_client.get("foo.baz"), b"bazqux"),
        )

        await self._bar_client.delete("foo.*")

        await asserts.assert_awaitables(
            (self._foo_client.get("foo.bar"), b"foobar"),
            (self._foo_client.get("foo.baz"), b"foobar"),
            (self._bar_client.get("foo.bar"), None),
            (self._bar_client.get("foo.baz"), None),
        )

    async def test_hash(self, redis_client: aioredis.Redis) -> None:
        hash1 = self._foo_client.hash_("foobar")
        hash2 = self._bar_client.hash_("foobar")

        await asyncio.gather(
            hash1.set_("foobar", "foobar"),
            hash1.set_("bazqux", "foobar"),
            hash2.set_("foobar", "bazqux"),
            hash2.set_("bazqux", "bazqux"),
        )

        await asserts.assert_awaitables(
            (hash1.length(), 2),
            (hash2.length(), 2),
            (hash1.get("foobar"), b"foobar"),
            (hash2.get("foobar"), b"bazqux"),
            (
                asserts.assert_iterable(
                    hash1.to_iterable(),
                    [
                        (b"bazqux", b"foobar"),
                        (b"foobar", b"foobar"),
                    ],
                ),
                None,
            ),
            (
                asserts.assert_iterable(
                    hash2.to_iterable(),
                    [
                        (b"bazqux", b"bazqux"),
                        (b"foobar", b"bazqux"),
                    ],
                ),
                None,
            ),
        )

        await asyncio.gather(
            hash1.delete("foobar"),
            hash2.delete("foobar"),
            hash2.delete("bazqux"),
        )

        await asserts.assert_awaitables(
            (hash1.length(), 1),
            (hash2.length(), 0),
            (hash1.get("foobar"), None),
            (hash1.get("bazqux"), b"foobar"),
            (hash2.get("foobar"), None),
            (hash2.get("bazqux"), None),
        )

    async def test_list(self) -> None:
        list1 = self._foo_client.list_("foobar")
        list2 = self._bar_client.list_("foobar")

        await asyncio.gather(
            list1.push("foobar1"),
            list1.push("bazqux1"),
            list2.push("foobar2"),
            list2.push("bazqux2"),
        )

        await asserts.assert_iterable(
            list1.to_iterable(),
            [
                b"foobar1",
                b"bazqux1",
            ],
        )

        await asserts.assert_iterable(
            list2.to_iterable(),
            [
                b"foobar2",
                b"bazqux2",
            ],
        )

    @pytest.fixture(autouse=True)
    def _setup(self, redis_client: aioredis.Redis) -> None:
        self._foo_client = redis.Client(redis_client, "foo")
        self._bar_client = redis.Client(redis_client, "bar")
