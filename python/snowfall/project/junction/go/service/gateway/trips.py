from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Sequence

import prometheus_client
from grpc import aio

from snowfall.project.junction.go.service.gateway import providers, tasks
from snowfall.project.junction.go.service.gateway.v1 import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.provider.v2alpha import trips_pb2 as provider_trips_pb2
from snowfall.stdlib import string
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, protocol, types
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        producer: protocol.Producer,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
    ):
        self._producer = producer
        self._runner = runner

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def EnqueueTripSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripSearchResponse:
        trip_search_id = string.uuid()

        await asyncio.gather(
            self._producer.publish(
                trips_pb2.TripSearchTask(
                    id=trip_search_id,
                    one_way=request.one_way,
                    round_trip=request.round_trip,
                    multi_city=request.multi_city,
                    passengers=request.passengers,
                ),
                "tasks.trip_search",
            ),
            self._runner.mark_as_in_progress(trip_search_id),
        )

        return trips_pb2.EnqueueTripSearchResponse(id=trip_search_id)

    async def DrainTripSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.DrainTripSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.DrainTripSearchResultsResponse:
        return trips_pb2.DrainTripSearchResultsResponse(
            is_in_progress=await self._runner.is_in_progress(request.id),
            results=await self._runner.drain_results(request.id),
        )


class Queue(consumer.AbstractQueue[trips_pb2.TripSearchTask]):
    def __init__(
        self,
        name_prefix: str,
        providers_list: providers.Collection,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
        timeout: datetime.timedelta,
    ):
        self._name_prefix = name_prefix
        self._providers = providers_list
        self._runner = runner
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
        await self._runner.run(msg.body.id, self._on_message(msg.body))

    async def _on_message(
        self,
        body: trips_pb2.TripSearchTask,
    ) -> AsyncGenerator[trips_pb2.TripSearchResult, None]:
        search_tasks = [
            self._searcher.search(provider, body)
            async for provider in self._providers.all_healthy()
            if provider.trip_search_capabilities.is_supported
        ]

        for task in asyncio.as_completed(search_tasks):
            response: provider_trips_pb2.SearchTripsResponse = await task

            for search_result in response.results:
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
