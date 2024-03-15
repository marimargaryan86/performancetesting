from __future__ import annotations

import asyncio
import dataclasses
import datetime
from collections.abc import AsyncIterator, Callable
from typing import Generic, TypeVar

from aio_pika import abc
from aiostream import stream
from grpc import aio

from snowfall.project.junction.rocket.provider import repository
from snowfall.project.junction.rocket.provider.v1alpha import (
    searches_pb2,
    searches_pb2_grpc,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    amqp_pb2 as searches_amqp_pb2,
)
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    models_pb2 as legacy_searches_pb2,
)
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis
from snowfall.stdlib.transport.amqp import consumer as amqp_consumer
from snowfall.stdlib.transport.amqp import producer as amqp_producer
from snowfall.stdlib.transport.amqp import trackable
from snowfall.stdlib.transport.amqp import types as amqp_types
from snowfall.stdlib.transport.grpc import service

_SearchCriteria = TypeVar("_SearchCriteria", bound=object)
SearchCriteriaTaskGenerator = Callable[
    [legacy_searches_pb2.Search],
    list[_SearchCriteria],
]
SearchResultGenerator = Callable[
    [_SearchCriteria],
    AsyncIterator[legacy_searches_pb2.SearchResult],
]
_DEFAULT_ALLOWED_WINDOW_TD = datetime.timedelta(minutes=0)


@dataclasses.dataclass(frozen=True)
class SearchImplementation(Generic[_SearchCriteria]):
    search_criteria_task_generator: SearchCriteriaTaskGenerator[_SearchCriteria]
    search_result_cache_key_generator: repository.CacheKeyGenerator[_SearchCriteria]
    search_result_generator: repository.SearchResultGenerator[_SearchCriteria]
    allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD


class Searcher(Generic[_SearchCriteria]):
    _search_timeout_s = 50  # noqa: WPS432

    def __init__(
        self,
        task_generator: SearchCriteriaTaskGenerator[_SearchCriteria],
        search_result_repository: repository.SearchResultRepository[_SearchCriteria],
        allowed_window_td: datetime.timedelta = _DEFAULT_ALLOWED_WINDOW_TD,
    ):
        self._allowed_window_td = allowed_window_td
        self._search_result_repository = search_result_repository
        self._search_criteria_task_generator = task_generator
        self._logger = stdout.get_logger()

    @classmethod
    def from_implementation(
        cls,
        implementation: SearchImplementation[_SearchCriteria],
        redis_client: redis.Client[bytes],
    ) -> Searcher[_SearchCriteria]:
        return cls(
            task_generator=implementation.search_criteria_task_generator,
            allowed_window_td=implementation.allowed_window_td,
            search_result_repository=repository.SearchResultRepository(
                search_result_cache_key_func=implementation.search_result_cache_key_generator,
                redis=redis_client,
                search_result_generator=implementation.search_result_generator,
            ),
        )

    async def search(
        self,
        search: legacy_searches_pb2.Search,
    ) -> AsyncIterator[legacy_searches_pb2.SearchResult]:
        search_criterion_tasks = self._search_criteria_task_generator(search)
        generators = [
            self._process_search_task(search_criterion_task)
            for search_criterion_task in search_criterion_tasks
        ]

        if not generators:
            return

        async with stream.merge(*generators).stream() as search_results:
            async for search_result in search_results:
                yield search_result

    async def _process_search_task(
        self,
        task: _SearchCriteria,
    ) -> AsyncIterator[legacy_searches_pb2.SearchResult]:
        search_results = self._search_result_repository.find(task)
        try:
            # Timeout and return here, so if there are completed tasks in .search()
            # it can still return a partial result.
            async with asyncio.timeout(self._search_timeout_s):
                async for search_result in search_results:
                    yield search_result
        except TimeoutError:
            self._logger.warning("Search matching timed out.")


class SearchService(service.Service, searches_pb2_grpc.SearchServiceServicer):
    def __init__(
        self,
        searcher: Searcher[_SearchCriteria],
        provider_name: str,
    ):
        self._provider_name = provider_name
        self._searcher = searcher

    def get_name(self) -> str:
        return searches_pb2.DESCRIPTOR.services_by_name["SearchService"].full_name

    def register(self, server: aio.Server) -> None:
        searches_pb2_grpc.add_SearchServiceServicer_to_server(self, server)

    async def Search(  # type: ignore[override] # noqa: N802
        self,
        request: searches_pb2.SearchRequest,
        context: aio.ServicerContext,
    ) -> searches_pb2.SearchResponse:
        return searches_pb2.SearchResponse(
            search_results=searches_pb2.SearchResults(
                search_task_results=[
                    searches_amqp_pb2.SearchTaskResult(
                        search_id=request.search_task.search_id,
                        search_result=search_result,
                    )
                    async for search_result in self._searcher.search(
                        request.search_task.search,
                    )
                ],
            ),
        )


class SearchConsumer(Generic[_SearchCriteria]):
    def __init__(
        self,
        consumer: amqp_consumer.Consumer[searches_amqp_pb2.SearchTask],
        producer: amqp_producer.Producer,
        searcher: Searcher[_SearchCriteria],
        provider_name: str,
        provider_id: str,
    ):
        self._consumer = consumer
        self._producer = producer
        self._searcher = searcher
        self._provider_name = provider_name
        self._provider_id = provider_id

    async def consume(self) -> None:
        await self._consumer.consume(self._process_message)

    async def _process_message(
        self,
        amqp_message: amqp_types.Message[searches_amqp_pb2.SearchTask],
    ) -> None:
        await self._publish_search_task_results(amqp_message)

    async def _publish_search_task_results(
        self,
        amqp_message: amqp_types.Message[searches_amqp_pb2.SearchTask],
    ) -> None:
        search_results = self._searcher.search(
            amqp_message.body.search,
        )

        async for search_result in search_results:
            await self._producer.publish(
                msg=searches_amqp_pb2.SearchTaskResult(
                    search_id=amqp_message.body.search_id,
                    search_result=search_result,
                ),
                routing_key="searches",
            )


def create_search_consumer(
    amqp_connection: abc.AbstractConnection,
    redis_client: redis.Client[bytes],
    implementation: SearchImplementation[_SearchCriteria],
    app_name: str,
    provider_name: str,
    provider_id: str,
) -> SearchConsumer[_SearchCriteria]:
    producer = amqp_producer.Producer(
        connection=amqp_connection,
        exchange=amqp_types.Exchange("searches"),
    )

    return SearchConsumer(
        consumer=amqp_consumer.Consumer(
            connection=amqp_connection,
            queue_name="{0}_searches".format(app_name),
            binds=[
                (amqp_types.Exchange("searches"), "searches"),
            ],
            middleware_stack=[
                trackable.ReportingMiddleware(
                    status_reporter=trackable.StatusReporter(
                        producer=producer,
                    ),
                ).execute,
            ],
        ),
        producer=producer,
        searcher=Searcher.from_implementation(
            implementation=implementation,
            redis_client=redis_client,
        ),
        provider_name=provider_name,
        provider_id=provider_id,
    )
