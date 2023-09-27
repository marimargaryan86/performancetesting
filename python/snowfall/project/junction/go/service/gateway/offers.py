from __future__ import annotations

import asyncio
import datetime
import time
from collections.abc import AsyncGenerator, Sequence

import prometheus_client
from grpc import StatusCode, aio

from snowfall.project.junction.go.service.gateway import providers, tasks
from snowfall.project.junction.go.service.gateway.v1 import (
    offers_pb2,
    offers_pb2_grpc,
)
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2
from snowfall.project.junction.provider.v1alpha import offers_pb2 as providers_pb2
from snowfall.stdlib.instrumentation import prometheus
from snowfall.stdlib.logging import stdout
from snowfall.stdlib.transport.amqp import consumer, protocol
from snowfall.stdlib.transport.amqp import types as amqp
from snowfall.stdlib.transport.grpc import service

_logger = stdout.get_logger()
_failed = prometheus_client.Counter(
    "gateway_failed_trip_offer_searches_total",
    "Total number of failed trip offer searches",
    ["provider_id"],
)

_histogram = prometheus_client.Histogram(
    "gateway_trip_offer_search_duration_seconds",
    "Duration of performed trip offer searches in seconds",
    ["provider_id", "status"],
    buckets=prometheus.BUCKETS,
)

_total = prometheus_client.Counter(
    "gateway_trip_offer_searches_total",
    "Total number of performed trip offer searches",
    ["provider_id", "status"],
)


class Service(service.Service, offers_pb2_grpc.OfferServiceServicer):
    def __init__(
        self,
        producer: protocol.Producer,
        runner: tasks.Runner[amqp_pb2.TripOfferSearchResult],
    ):
        self._producer = producer
        self._runner = runner

    def get_name(self) -> str:
        return offers_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: aio.Server) -> None:
        offers_pb2_grpc.add_OfferServiceServicer_to_server(self, server)

    async def EnqueueOfferSearch(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.EnqueueOfferSearchRequest,
        context: aio.ServicerContext,
    ) -> offers_pb2.EnqueueOfferSearchResponse:
        match request.WhichOneof("offer_search_task"):
            case "trip_offer_search_task":
                await asyncio.gather(
                    self._producer.publish(
                        request.trip_offer_search_task,
                        "offers.search.trip",
                    ),
                    self._runner.mark_as_in_progress(
                        request.trip_offer_search_task.offer_search_id,
                    ),
                )

                identifier = request.trip_offer_search_task.offer_search_id
            case _:
                await context.abort(StatusCode.UNIMPLEMENTED)
                raise RuntimeError() from None  # TODO: Remove when grpcio types are available.

        return offers_pb2.EnqueueOfferSearchResponse(id=identifier)

    async def PopOfferSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.PopOfferSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> offers_pb2.PopOfferSearchResultsResponse:
        return offers_pb2.PopOfferSearchResultsResponse(
            is_in_progress=await self._runner.is_in_progress(request.id),
            trip_offer_search_results=offers_pb2.TripOfferSearchResults(
                results=await self._runner.drain_results(request.id),
            ),
        )


class Queue(consumer.AbstractQueue[amqp_pb2.TripOfferSearchTask]):
    def __init__(
        self,
        name_prefix: str,
        providers_list: providers.Collection,
        runner: tasks.Runner[amqp_pb2.TripOfferSearchResult],
        timeout: datetime.timedelta,
    ):
        self._name_prefix = name_prefix
        self._providers = providers_list
        self._runner = runner
        self._timeout = timeout

    @property
    def binds(self) -> Sequence[tuple[amqp.Exchange, str]]:
        return [
            (amqp.Exchange(self._name_prefix), "offers.search.*"),
        ]

    @property
    def name(self) -> str:
        return "{0}_offer_searches".format(self._name_prefix)

    async def on_message(self, msg: amqp.Message[amqp_pb2.TripOfferSearchTask]) -> None:
        match msg.body:
            case amqp_pb2.TripOfferSearchTask():
                await self._runner.run(
                    msg.body.offer_search_id,
                    self._consume_trip_task(msg.body),
                )

    async def _consume_trip_task(  # noqa: WPS210
        self,
        msg: amqp_pb2.TripOfferSearchTask,
    ) -> AsyncGenerator[amqp_pb2.TripOfferSearchResult, None]:
        search_tasks = [
            _do_trip_offer_search(provider, msg, self._timeout)
            async for provider in self._providers.all_healthy()
        ]

        for task in asyncio.as_completed(search_tasks):
            search_result: providers_pb2.SearchOffersResponse = await task

            for offer in search_result.trip_offer_search_results.results:
                yield offer


async def _do_trip_offer_search(
    provider: providers.Provider,
    msg: amqp_pb2.TripOfferSearchTask,
    timeout: datetime.timedelta,
) -> providers_pb2.SearchOffersResponse:
    start = time.perf_counter()
    status = "ok"

    try:
        response = await provider.connection.offers.SearchOffers(
            providers_pb2.SearchOffersRequest(trip_offer_search_task=msg),
            timeout=timeout.total_seconds(),
        )
    except aio.AioRpcError:
        _failed.labels(provider_id=provider.identifier).inc()
        response = providers_pb2.SearchOffersResponse()
        status = "nok"
    finally:
        exec_time = time.perf_counter() - start

    _histogram.labels(provider_id=provider.identifier, status=status).observe(exec_time)
    _total.labels(provider_id=provider.identifier, status=status).inc()
    _logger.info(
        "trip offer search performed",
        provider_id=provider.identifier,
        failed=status == "nok",
        results=len(response.trip_offer_search_results.results),
        execution_time=exec_time,
    )

    return response
