from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Mapping, Sequence

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
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.service import tasks
from snowfall.stdlib.transport.amqp import consumer, protocol
from snowfall.stdlib.transport.amqp import types as amqp
from snowfall.stdlib.transport.grpc import service

_logger = stdout.get_logger()


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
                "searches.search",
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
            search_task_results=await self._runner.drain_results(request.id),
        )


class Queue(consumer.AbstractQueue[amqp_pb2.SearchTask]):
    def __init__(
        self,
        name_prefix: str,
        providers_list: providers.Collection,
        runner: tasks.Runner[amqp_pb2.SearchTaskResult],
        timeout: datetime.timedelta,
        reseller_providers: Mapping[str, Sequence[str]],
    ):
        self._name_prefix = name_prefix
        self._providers = providers_list
        self._runner = runner
        self._timeout = timeout
        self._reseller_providers = reseller_providers

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
            if self._provider_can_handle(msg, provider)
        ]

        for task in asyncio.as_completed(search_tasks):
            response: providers_pb2.SearchResponse = await task

            for search_task_result in response.search_results.search_task_results:
                search_task_result.search_result.search_id = (
                    search_task_result.search_id
                )
                yield search_task_result

    def _provider_can_handle(
        self,
        msg: amqp_pb2.SearchTask,
        provider: providers.Provider,
    ) -> bool:
        if not provider.has_search_capability_for(msg):
            return False

        return self._provider_on_for_reseller(
            provider.identifier,
            msg.search.reseller_id,
        )

    def _provider_on_for_reseller(
        self,
        provider_id: str,
        reseller_id: str,
    ) -> bool:
        provider_on_for_all = provider_id in self._reseller_providers.get("*", [])
        provider_on_for_reseller = provider_id in self._reseller_providers.get(
            reseller_id,
            [],
        )

        return provider_on_for_all or provider_on_for_reseller


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

        response = providers_pb2.SearchResponse()
        status = "nok"
    finally:
        exec_time = time.perf_counter() - start

    _logger.info(
        "search performed",
        provider_id=provider.identifier,
        failed=status == "nok",
        search_task_results=len(response.search_results.search_task_results),
        execution_time=exec_time,
    )

    return response
