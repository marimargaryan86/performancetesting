from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import Awaitable, Callable, Sequence

import prometheus_client
from grpc import aio

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.persistence.redis import types as redis_types
from snowfall.stdlib.transport.amqp import consumer, protocol, types
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(self, repository: Repository):
        self._repository = repository

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def EnqueueTripSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripSearchResponse:
        return trips_pb2.EnqueueTripSearchResponse(
            id=await self._repository.enqueue_task(
                trips_pb2.TripSearchTask(
                    id=string.uuid(),
                    one_way=request.one_way,
                    round_trip=request.round_trip,
                    multi_city=request.multi_city,
                    passengers=request.passengers,
                ),
            ),
        )

    async def DrainTripSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.DrainTripSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.DrainTripSearchResultsResponse:
        return trips_pb2.DrainTripSearchResultsResponse(
            is_in_progress=await self._repository.is_task_in_progress(request.id),
            results=await self._repository.drain_results_from_task(request.id),
        )


class Queue(consumer.AbstractQueue[trips_pb2.TripSearchTask]):
    def __init__(
        self,
        name_prefix: str,
        providers_list: providers.Collection,
        repository: Repository,
        timeout: datetime.timedelta,
    ):
        self._name_prefix = name_prefix
        self._providers = providers_list
        self._repository = repository
        self._searcher = Searcher(timeout)

    @property
    def binds(self) -> Sequence[tuple[types.Exchange, str]]:
        return [
            (types.Exchange(self._name_prefix), "trips.search.*"),
        ]

    @property
    def name(self) -> str:
        return "{0}_trip_searches".format(self._name_prefix)

    async def on_message(self, msg: types.Message[trips_pb2.TripSearchTask]) -> None:
        tasks = [
            self._searcher.search(provider, msg.body)
            async for provider in self._providers.all_healthy()
            if provider.trip_search_capabilities.is_supported
        ]

        async with asyncio.TaskGroup() as tg:
            for task in asyncio.as_completed(tasks):
                response: provider_trips_pb2.SearchTripsResponse = await task

                for search_result in response.results:
                    tg.create_task(  # type: ignore[unused-awaitable]
                        self._repository.add_result_to_task(msg.body.id, search_result),
                    )

        await self._repository.mark_task_as_done(msg.body.id)


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
        msg: trips_pb2.TripSearchTask,
    ) -> provider_trips_pb2.SearchTripsResponse:
        start = time.perf_counter()
        status = "ok"

        search_func: Callable[
            [providers.Provider, trips_pb2.TripSearchTask],
            Awaitable[provider_trips_pb2.SearchTripsResponse],
        ]

        match msg.WhichOneof("search_mode"):
            case "one_way":
                search_func = self._search_one_way
            case "round_trip":
                search_func = self._search_round_trip
            case "multi_city":
                search_func = self._search_multi_city
            case _:
                return provider_trips_pb2.SearchTripsResponse()

        try:
            response = await search_func(provider, msg)
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

    async def _search_one_way(
        self,
        provider: providers.Provider,
        msg: trips_pb2.TripSearchTask,
    ) -> provider_trips_pb2.SearchTripsResponse:
        return await provider.connection.offers.SearchOffers(
            provider_trips_pb2.SearchTripsRequest(
                one_way=provider_trips_pb2.SearchTripsRequest.OneWay(
                    criterion=provider_trips_pb2.SearchTripsRequest.Criterion(
                        # @todo: origin and destination logic
                        departure_date=msg.one_way.criterion.departure_date,
                    ),
                ),
                passengers=[
                    provider_trips_pb2.SearchTripsRequest.Passenger(
                        date_of_birth=passenger.date_of_birth,
                    )
                    for passenger in msg.passengers
                ],
            ),
            timeout=self._timeout.total_seconds(),
        )

    async def _search_round_trip(
        self,
        provider: providers.Provider,
        msg: trips_pb2.TripSearchTask,
    ) -> provider_trips_pb2.SearchTripsResponse:
        return provider_trips_pb2.SearchTripsResponse()

    async def _search_multi_city(
        self,
        provider: providers.Provider,
        msg: trips_pb2.TripSearchTask,
    ) -> provider_trips_pb2.SearchTripsResponse:
        return provider_trips_pb2.SearchTripsResponse()


class Repository(object):
    def __init__(self, producer: protocol.Producer, client: redis_types.Client[bytes]):
        self._trip_search_set = client.set_("trips.pending_searches")
        self._producer = producer
        self._redis_client = client

    async def add_result_to_task(
        self,
        identifier: str,
        search_result: provider_trips_pb2.Result,
    ) -> None:
        await self._results_list(identifier).push(
            protobuf.AnySerializer[trips_pb2.TripSearchResult].serialize(
                trips_pb2.TripSearchResult(
                    id=string.uuid(),
                    result=search_result,
                ),
            ),
        )

    async def enqueue_task(self, task: trips_pb2.TripSearchTask) -> str:
        await asyncio.gather(
            self._producer.publish(task, "tasks.trip_search"),
            self._trip_search_set.add(task.id),
        )

        return task.id

    async def is_task_in_progress(self, identifier: str) -> bool:
        return await self._trip_search_set.has(identifier)

    async def mark_task_as_done(self, identifier: str) -> None:
        await self._trip_search_set.remove(identifier)

    async def drain_results_from_task(
        self,
        identifier: str,
    ) -> list[trips_pb2.TripSearchResult]:
        return [
            protobuf.AnySerializer[trips_pb2.TripSearchResult].deserialize(trip_result)
            for trip_result in await self._results_list(identifier).pop(
                await self._results_list(identifier).length(),
            )
        ]

    def _results_list(self, identifier: str) -> redis_types.List[bytes]:
        return self._redis_client.list_("trips.results.{0}".format(identifier))
