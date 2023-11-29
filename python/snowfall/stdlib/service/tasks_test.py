from __future__ import annotations

import datetime
from collections.abc import AsyncGenerator

import pytest
from google.protobuf import json_format
from redis import asyncio as aioredis

from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.service import tasks
from snowfall.stdlib.testing import asserts
from snowfall.stdlib.v1 import testing_pb2


@pytest.fixture()
def test_runner(
    redis_client: aioredis.Redis[bytes],
) -> tasks.Runner[testing_pb2.Foobar]:
    return tasks.Runner[testing_pb2.Foobar](
        client=types.Client(redis_client),
        ttl=datetime.timedelta(hours=1),
        gc_probability=1,
    )


@pytest.fixture()
def test_runner_without_ttl(
    redis_client: aioredis.Redis[bytes],
) -> tasks.Runner[testing_pb2.Foobar]:
    return tasks.Runner[testing_pb2.Foobar](
        client=types.Client(redis_client),
        ttl=datetime.timedelta(hours=-1),
        gc_probability=0,
    )


class TestRunner(object):
    async def test_can_run(self, test_runner: tasks.Runner[testing_pb2.Foobar]) -> None:
        await test_runner.mark_as_in_progress("foobar")
        await test_runner.run("foobar", _result_generator())
        assert not await test_runner.is_in_progress("foobar")
        await asserts.assert_iterable(
            [
                json_format.MessageToJson(task_result)
                for task_result in await test_runner.drain_results(
                    "foobar",
                )
            ],
            [
                json_format.MessageToJson(testing_pb2.Foobar(id="foobar")),
            ],
        )

    async def test_results_expire(
        self,
        test_runner_without_ttl: tasks.Runner[testing_pb2.Foobar],
    ) -> None:
        await test_runner_without_ttl.mark_as_in_progress("foobar")
        assert not await test_runner_without_ttl.is_in_progress("foobar")

        await test_runner_without_ttl.run("foobar", _result_generator())
        assert not await test_runner_without_ttl.drain_results("foobar")

    async def test_garbage_collection_is_cleaning_up_expired_tasks(
        self,
        test_runner_without_ttl: tasks.Runner[testing_pb2.Foobar],
        test_runner: tasks.Runner[testing_pb2.Foobar],
    ) -> None:
        await test_runner_without_ttl.mark_as_in_progress("foobar")
        await test_runner.mark_as_in_progress("foobar_with_ttl")
        assert await test_runner.is_in_progress("foobar_with_ttl")
        assert not await test_runner.is_in_progress("foobar")


async def _result_generator() -> AsyncGenerator[testing_pb2.Foobar, None]:
    yield testing_pb2.Foobar(id="foobar")
