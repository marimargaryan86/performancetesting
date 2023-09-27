from __future__ import annotations

import asyncio
import datetime
import secrets
from collections.abc import AsyncGenerator
from typing import Generic, TypeVar

from google.protobuf import message

from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types

_TaskResult = TypeVar("_TaskResult", bound=message.Message)
_TaskResultGenerator = AsyncGenerator[_TaskResult, None]


class Runner(Generic[_TaskResult]):
    def __init__(
        self,
        client: types.Client[bytes],
        *,
        ttl: datetime.timedelta,
        gc_probability: float,
    ):
        self._repository = _ResultRepository[_TaskResult](client=client, ttl=ttl)
        self._state_manager = _StateManager(
            client=client,
            ttl=ttl,
            gc_probability=gc_probability,
        )

    async def drain_results(self, identifier: str) -> list[_TaskResult]:
        return await self._repository.drain_from_task(identifier)

    async def is_in_progress(self, identifier: str) -> bool:
        return await self._state_manager.is_in_progress(identifier)

    async def mark_as_in_progress(self, identifier: str) -> None:
        return await self._state_manager.mark_as_in_progress(identifier)

    async def run(
        self,
        identifier: str,
        generator: _TaskResultGenerator[_TaskResult],
    ) -> None:
        async with asyncio.TaskGroup() as tg:
            async for task_result in generator:
                tg.create_task(  # type: ignore[unused-awaitable]
                    self._repository.add_to_task(identifier, task_result),
                )

        await self._state_manager.mark_as_done(identifier)


class _StateManager(object):
    def __init__(
        self,
        client: types.Client[bytes],
        *,
        ttl: datetime.timedelta,
        gc_probability: float,
    ):
        self._gc_probability = gc_probability
        self._in_progress_set = client.sorted_set("tasks.in_progress")
        self._ttl = ttl

    async def mark_as_in_progress(self, identifier: str) -> None:
        await self._in_progress_set.add(
            identifier,
            self._expires_at.timestamp(),
        )

    async def is_in_progress(self, identifier: str) -> bool:
        await self._maybe_do_garbage_collection()
        score = await self._in_progress_set.get_score(identifier)

        if not score:
            return False

        expiry = datetime.datetime.fromtimestamp(score, tz=datetime.UTC)
        return expiry > datetime.datetime.now(tz=datetime.UTC)

    async def mark_as_done(self, identifier: str) -> None:
        await self._in_progress_set.remove(identifier)

    async def _maybe_do_garbage_collection(self) -> None:
        if secrets.randbelow(100) > (self._gc_probability * 100):
            return

        await self._in_progress_set.remove_between_scores(
            min_=0,
            max_=datetime.datetime.now(tz=datetime.UTC).timestamp(),
        )

    @property
    def _expires_at(self) -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.UTC) + self._ttl


class _ResultRepository(Generic[_TaskResult]):
    def __init__(
        self,
        client: types.Client[bytes],
        *,
        ttl: datetime.timedelta,
    ):
        self._redis_client = client
        self._ttl = ttl

    async def add_to_task(
        self,
        identifier: str,
        task_result: _TaskResult,
    ) -> None:
        results_list = self._results_list(identifier)

        await results_list.push(
            protobuf.AnySerializer[_TaskResult].serialize(task_result),
        )

        await types.put_expires_at_if_less_than_current(
            self._redis_client,
            results_list,
            self._expires_at,
        )

    async def drain_from_task(self, identifier: str) -> list[_TaskResult]:
        results_list = self._results_list(identifier)

        return [
            protobuf.AnySerializer[_TaskResult].deserialize(task_result)
            for task_result in await results_list.pop(await results_list.length())
        ]

    def _results_list(self, identifier: str) -> types.List[bytes]:
        return self._redis_client.list_("tasks.results.{0}".format(identifier))

    @property
    def _expires_at(self) -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.UTC) + self._ttl
