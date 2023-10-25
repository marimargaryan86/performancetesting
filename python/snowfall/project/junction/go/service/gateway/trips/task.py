from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Sequence

import prometheus_client
from grpc import aio

from snowfall.project.junction.go.service.gateway import providers, tasks
from snowfall.project.junction.go.service.gateway.trips import request as trips_request
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.stdlib import string
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
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
            (types.Exchange(self._name_prefix), "trips.search.*"),
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


class Searcher(object):
    _failed = prometheus_client.Counter(
        "gateway_failed_trip_searches_total",
        "Total number of failed trip searches",
        ["provider_id"],
    )

    _histogram = prometheus_client.Histogram(
        "gateway_trip_search_duration_seconds",
        "Duration of performed trip searches in seconds",
        ["provider_id", "status"],
        buckets=prometheus.BUCKETS,
    )

    _total = prometheus_client.Counter(
        "gateway_trip_searches_total",
        "Total number of performed trip searches",
        ["provider_id", "status"],
    )

    def __init__(self, timeout: datetime.timedelta):
        self._logger = stdout.get_logger()
        self._timeout = timeout

    async def search(
        self,
        provider: providers.Provider,
        request: provider_trips_pb2.SearchTripsRequest,
    ) -> provider_trips_pb2.SearchTripsResponse:
        start = time.perf_counter()
        status = "ok"

        try:
            response = await provider.connection.trips.SearchTrips(
                request=request,
                timeout=self._timeout.total_seconds(),
            )
        except aio.AioRpcError:
            self._failed.labels(provider_id=provider.identifier).inc()
            response = provider_trips_pb2.SearchTripsResponse()
            status = "nok"
        finally:
            exec_time = time.perf_counter() - start

        self._histogram.labels(provider_id=provider.identifier, status=status).observe(
            exec_time,
        )
        self._total.labels(provider_id=provider.identifier, status=status).inc()
        self._logger.info(
            "trip search performed",
            provider_id=provider.identifier,
            failed=status == "nok",
            results=len(response.results),
            execution_time=exec_time,
        )

        return response
