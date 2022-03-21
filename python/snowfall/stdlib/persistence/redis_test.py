import asyncio
import datetime

import aioredis
import freezegun
import pytest

from snowfall.stdlib.persistence import redis
from snowfall.stdlib.testing import asserts


@pytest.mark.asyncio
class TestPrefixClient(object):
    async def test_set_get_delete(self, redis_client: aioredis.Redis) -> None:
        await asyncio.gather(
            self._foo_client.put("foobar", "foobar"),
            self._bar_client.put("foobar", "bazqux"),
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
            self._foo_client.put("foo.bar", "foobar"),
            self._foo_client.put("foo.baz", "foobar"),
            self._bar_client.put("foo.bar", "bazqux"),
            self._bar_client.put("foo.baz", "bazqux"),
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
            hash1.put("foobar", "foobar"),
            hash1.put("bazqux", "foobar"),
            hash2.put("foobar", "bazqux"),
            hash2.put("bazqux", "bazqux"),
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

    async def test_set(self) -> None:
        set1 = self._foo_client.set_("foobar")
        set2 = self._bar_client.set_("foobar")

        await asyncio.gather(
            set1.add("foo1"),
            set1.add("baz1"),
            set2.add("foo2"),
            set2.add("baz2"),
        )

        await asserts.assert_iterable(
            set1.to_iterable(),
            [
                b"foo1",
                b"baz1",
            ],
        )

        await asserts.assert_iterable(
            set2.to_iterable(),
            [
                b"foo2",
                b"baz2",
            ],
        )

    @freezegun.freeze_time("2021-12-21 12:12:12.121212")
    async def test_expire_in_set(self) -> None:
        set1 = self._foo_client.set_("foobar")
        set2 = self._bar_client.set_("foobar")

        await asyncio.gather(
            set1.add("foo"),
            set2.add("foo"),
        )

        expiry = datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(seconds=30)

        await self._foo_client.put_expires_at(set1, expiry)

        await asserts.assert_awaitables(
            (self._foo_client.get_expires_at(set1), expiry),
            (self._bar_client.get_expires_at(set2), None),
        )

    @freezegun.freeze_time("2021-12-21 12:12:12.121212")
    async def test_put_expires_at_client(self) -> None:
        await asyncio.gather(
            self._foo_client.put("foo", "bar"),
            self._bar_client.put("foo", "bar"),
        )

        expiry = datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(seconds=30)

        await self._foo_client.put_expires_at("foo", expiry)

        await asserts.assert_awaitables(
            (self._foo_client.get_expires_at("foo"), expiry),
            (self._bar_client.get_expires_at("foo"), None),
        )

    @freezegun.freeze_time("2021-12-21 12:12:12.121212")
    async def test_put_expires_at_if_greater(self) -> None:
        set1 = self._foo_client.set_("foobar")
        set2 = self._bar_client.set_("foobar")

        expiry = datetime.datetime.now(
            tz=datetime.timezone.utc,
        ) + datetime.timedelta(seconds=30)

        await asyncio.gather(
            set1.add("foo"),
            set2.add("foo"),
            redis.put_expires_at_if_greater(self._foo_client, set1, expiry),
            redis.put_expires_at_if_greater(
                self._foo_client,
                set1,
                datetime.datetime.now(
                    tz=datetime.timezone.utc,
                )
                + datetime.timedelta(seconds=10),
            ),
        )

        await asserts.assert_awaitables(
            (self._foo_client.get_expires_at(set1), expiry),
            (self._bar_client.get_expires_at(set2), None),
        )

    @pytest.fixture(autouse=True)
    def _setup(self, redis_client: aioredis.Redis) -> None:
        self._foo_client = redis.Client[bytes](redis_client, "foo")
        self._bar_client = redis.Client[bytes](redis_client, "bar")
