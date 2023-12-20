from __future__ import annotations

import asyncio
import contextlib
import datetime
import time
from collections.abc import AsyncGenerator, Sequence
from types import TracebackType
from typing import NamedTuple

import prometheus_client
from grpc import aio

from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.project.junction.service.gateway import providers
from snowfall.project.junction.service.gateway.trips import cache as trips_cache
from snowfall.project.junction.service.gateway.trips import (
    request as trips_request,
)
from snowfall.project.junction.service.gateway.v1 import trips_pb2
from snowfall.stdlib import string
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import tasks
from snowfall.stdlib.transport.amqp import consumer, types


class Queue(consumer.AbstractQueue[trips_pb2.TripSearchTask]):
    def __init__(
        self,
        name_prefix: str,
        request_generator: trips_request.Generator,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
        searcher: Searcher,
    ):
        self._request_generator = request_generator
        self._name_prefix = name_prefix
        self._runner = runner
        self._searcher = searcher

    @property
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        return [
            (types.Exchange(self._name_prefix), "tasks.trip_search"),
        ]

    @property
    def name(self) -> str:
        return "{0}_trip_searches".format(self._name_prefix)

    async def on_message(self, msg: types.Message[trips_pb2.TripSearchTask]) -> None:
        await self._runner.run(msg.body.id, self._on_message(msg.body))

    async def _on_message(
        self,
        body: trips_pb2.TripSearchTask,
    ) -> AsyncGenerator[trips_pb2.TripSearchResult, None]:
        search_tasks = [
            self._searcher.search(provider, request)
            async for provider, request in self._request_generator.generate(body)
        ]

        for task in asyncio.as_completed(search_tasks):
            for search_result in (await task).results:
                yield trips_pb2.TripSearchResult(
                    id=string.uuid(),
                    result=search_result,
                )


class _Metrics(contextlib.AbstractContextManager["_Metrics"]):
    _cached = prometheus_client.Counter(
        "gateway_cached_trip_searches_total",
        "Total number of cached trip searches",
        ["provider_id"],
    )

    _failed = prometheus_client.Counter(
        "gateway_failed_trip_searches_total",
        "Total number of failed trip searches",
        ["provider_id"],
    )

    _histogram = prometheus_client.Histogram(
        "gateway_trip_search_duration_seconds",
        "Duration of performed trip searches in seconds",
        ["provider_id", "status", "cached"],
        buckets=prometheus.BUCKETS,
    )

    _total = prometheus_client.Counter(
        "gateway_trip_searches_total",
        "Total number of performed trip searches",
        ["provider_id", "status", "cached"],
    )

    def __init__(self, provider: providers.Provider) -> None:
        self._logger = stdout.get_logger()
        self._provider = provider
        self._start = time.perf_counter()
        self.return_tuple = _SearchReturn(
            cached=False,
            failed=True,
            response=provider_trips_pb2.SearchTripsResponse(),
        )

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        exec_time = time.perf_counter() - self._start
        status = "nok" if self.return_tuple.failed else "ok"
        cached = "yes" if self.return_tuple.cached else "no"

        if self.return_tuple.failed:
            self._failed.labels(provider_id=self._provider.identifier).inc()

        if self.return_tuple.cached:
            self._cached.labels(provider_id=self._provider.identifier).inc()

        self._histogram.labels(
            cached=cached,
            provider_id=self._provider.identifier,
            status=status,
        ).observe(amount=exec_time)

        self._total.labels(
            cached=cached,
            provider_id=self._provider.identifier,
            status=status,
        ).inc()

        self._logger.info(
            "trip search performed",
            provider_id=self._provider.identifier,
            failed=self.return_tuple.failed,
            cached=self.return_tuple.cached,
            results=len(self.return_tuple.response.results),
            execution_time=exec_time,
        )


class _SearchReturn(NamedTuple):
    cached: bool
    failed: bool
    response: provider_trips_pb2.SearchTripsResponse


class Searcher(object):
    def __init__(
        self,
        cache_factory: trips_cache.Factory,
        timeout: datetime.timedelta,
    ) -> None:
        self._cache_factory = cache_factory
        self._timeout = timeout

    async def search(
        self,
        provider: providers.Provider,
        request: provider_trips_pb2.SearchTripsRequest,
    ) -> provider_trips_pb2.SearchTripsResponse:
        with _Metrics(provider=provider) as metrics:
            return_tuple = await self._search(provider, request)
            metrics.return_tuple = return_tuple

            return return_tuple.response

    async def _search(
        self,
        provider: providers.Provider,
        request: provider_trips_pb2.SearchTripsRequest,
    ) -> _SearchReturn:
        cache = self._cache_factory.create(provider=provider, request=request)
        response_or_none = await cache.get()

        if response_or_none and response_or_none.results:
            return _SearchReturn(cached=True, failed=False, response=response_or_none)

        async with cache.lock():
            response_or_none = await cache.get()

            if response_or_none and response_or_none.results:
                return _SearchReturn(
                    cached=True,
                    failed=False,
                    response=response_or_none,
                )

            try:
                response = await provider.connection.trips.SearchTrips(
                    request=request,
                    timeout=self._timeout.total_seconds(),
                )
            except aio.AioRpcError:
                # TODO(jyggen): log gRPC errors?
                return _SearchReturn(
                    cached=False,
                    failed=True,
                    response=provider_trips_pb2.SearchTripsResponse(),
                )

            await cache.put(response)

            return _SearchReturn(cached=False, failed=False, response=response)
