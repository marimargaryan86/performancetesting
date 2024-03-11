from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Sequence

import prometheus_client
from grpc import StatusCode, aio

from snowfall.project.junction.rocket.provider.v1alpha import (
    searches_pb2 as providers_pb2,
)
from snowfall.project.junction.rocket.service.gateway import providers
from snowfall.project.junction.rocket.service.gateway.v1alpha import (
    searches_pb2,
    searches_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import amqp_pb2
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import tasks
from snowfall.stdlib.transport.amqp import consumer, protocol
from snowfall.stdlib.transport.amqp import types as amqp
from snowfall.stdlib.transport.grpc import service

_logger = stdout.get_logger()
_failed = prometheus_client.Counter(
    "gateway_searches_total",
    "Total number of failed searches",
    ["provider_id"],
)

_histogram = prometheus_client.Histogram(
    "gateway_search_duration_seconds",
    "Duration of performed searches in seconds",
    ["provider_id", "status"],
    buckets=prometheus.BUCKETS,
)

_total = prometheus_client.Counter(
    "gateway_searches_total",
    "Total number of performed searches",
    ["provider_id", "status"],
)


class Service(service.Service, searches_pb2_grpc.SearchServiceServicer):
    def __init__(
        self,
        producer: protocol.Producer,
        runner: tasks.Runner[amqp_pb2.SearchTaskResult],
    ):
        self._producer = producer
        self._runner = runner

    def get_name(self) -> str:
        return searches_pb2.DESCRIPTOR.services_by_name["SearchService"].full_name

    def register(self, server: aio.Server) -> None:
        searches_pb2_grpc.add_SearchServiceServicer_to_server(self, server)

    async def EnqueueSearch(  # type: ignore[override] # noqa: N802
        self,
        request: searches_pb2.EnqueueSearchRequest,
        context: aio.ServicerContext,
    ) -> searches_pb2.EnqueueSearchResponse:
        await asyncio.gather(
            self._producer.publish(
                request.search_task,
                "searches",
            ),
            self._runner.mark_as_in_progress(
                request.search_task.search_id,
            ),
        )
        identifier = request.search_task.search_id

        return searches_pb2.EnqueueSearchResponse(id=identifier)

    async def PopSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: searches_pb2.PopSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> searches_pb2.PopSearchResultsResponse:
        return searches_pb2.PopSearchResultsResponse(
            is_in_progress=await self._runner.is_in_progress(request.id),
            results=await self._runner.drain_results(request.id),
        )


class Queue(consumer.AbstractQueue[amqp_pb2.SearchTask]):
    def __init__(
        self,
        name_prefix: str,
        providers_list: providers.Collection,
        runner: tasks.Runner[amqp_pb2.SearchTaskResult],
        timeout: datetime.timedelta,
    ):
        self._name_prefix = name_prefix
        self._providers = providers_list
        self._runner = runner
        self._timeout = timeout

    @property
    def binds(self) -> Sequence[tuple[amqp.Exchange, str]]:
        return [
            (amqp.Exchange(self._name_prefix), "searches.*"),
        ]

    @property
    def name(self) -> str:
        return "{0}_searches".format(self._name_prefix)

    async def on_message(
        self,
        msg: amqp.Message[amqp_pb2.SearchTask],
    ) -> None:
        await self._runner.run(
            msg.body.search_id,
            self._consume_search_task(msg.body),
        )

    async def _consume_search_task(
        self,
        msg: amqp_pb2.SearchTask,
    ) -> AsyncGenerator[amqp_pb2.SearchTaskResult, None]:
        search_tasks = [
            _do_search(provider, msg, self._timeout)
            async for provider in self._providers.all_healthy()
        ]

        for task in asyncio.as_completed(search_tasks):
            search_response: providers_pb2.SearchResponse = await task

            for search_result in search_response.search_results.results:
                yield search_result


async def _do_search(
    provider: providers.Provider,
    msg: amqp_pb2.SearchTask,
    timeout: datetime.timedelta,
) -> providers_pb2.SearchResponse:
    start = time.perf_counter()
    status = "ok"

    try:
        response = await provider.connection.searches.Search(
            providers_pb2.SearchRequest(
                search_task=msg,
            ),
            timeout=timeout.total_seconds(),
        )

    except aio.AioRpcError as ex:
        if ex.code() != StatusCode.UNIMPLEMENTED:
            _logger.exception("Provider search failed")

        _failed.labels(provider_id=provider.identifier).inc()
        response = providers_pb2.SearchResponse()
        status = "nok"
    finally:
        exec_time = time.perf_counter() - start

    _histogram.labels(provider_id=provider.identifier, status=status).observe(exec_time)
    _total.labels(provider_id=provider.identifier, status=status).inc()
    _logger.info(
        "search performed",
        provider_id=provider.identifier,
        failed=status == "nok",
        results=len(response.search_results),
        execution_time=exec_time,
    )

    return response
