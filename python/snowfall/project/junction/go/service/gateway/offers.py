from __future__ import annotations

import asyncio
import datetime
from typing import TypeVar

from google.protobuf import message
from grpc import StatusCode, aio

from snowfall.project.junction.go.service.gateway import providers
from snowfall.project.junction.go.service.gateway.v1alpha import (
    offers_pb2,
    offers_pb2_grpc,
)
from snowfall.project.junction.go.service.offers.v1 import amqp_pb2
from snowfall.project.junction.provider.v1alpha import offers_pb2 as providers_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.redis import types
from snowfall.stdlib.transport.amqp import protocol
from snowfall.stdlib.transport.amqp import types as amqp
from snowfall.stdlib.transport.grpc import service

_Proto = TypeVar("_Proto", bound=message.Message)


class Service(service.Service, offers_pb2_grpc.OfferServiceServicer):
    def __init__(self, repository: Repository):
        self._repository = repository

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
                identifier = await self._repository.enqueue_trip_task(
                    request.trip_offer_search_task,
                )
            case _:
                await context.abort(StatusCode.UNIMPLEMENTED)

        return offers_pb2.EnqueueOfferSearchResponse(id=identifier)

    async def PopOfferSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.PopOfferSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> offers_pb2.PopOfferSearchResultsResponse:
        return offers_pb2.PopOfferSearchResultsResponse(
            is_in_progress=await self._repository.is_in_progress(request.id),
            trip_offer_search_results=offers_pb2.TripOfferSearchResults(
                results=await self._repository.pop_offers(request.id),
            ),
        )


class Consumer(object):
    def __init__(
        self,
        providers_list: providers.Collection,
        repository: Repository,
        timeout: datetime.timedelta,
    ):
        self._providers = providers_list
        self._repository = repository
        self._timeout = timeout

    async def consume(self, msg: amqp.Message[amqp_pb2.TripOfferSearchTask]) -> None:
        match msg.body:
            case amqp_pb2.TripOfferSearchTask():
                await self._consume_trip_task(msg.body)

    async def _consume_trip_task(  # noqa: WPS210
        self,
        msg: amqp_pb2.TripOfferSearchTask,
    ) -> None:
        tasks = []

        async for provider in self._providers.all_():
            tasks.append(_do_trip_offer_search(provider, msg, self._timeout))

        async with asyncio.TaskGroup() as tg:
            for task in asyncio.as_completed(tasks):
                search_result: providers_pb2.SearchOffersResponse = await task

                for offer in search_result.trip_offer_search_results.results:
                    tg.create_task(  # type: ignore[unused-awaitable]
                        self._repository.add_offer(
                            msg.offer_search_id,
                            offer,
                        ),
                    )

        await self._repository.mark_as_done(msg.offer_search_id)


async def _do_trip_offer_search(
    provider: providers.Provider,
    msg: amqp_pb2.TripOfferSearchTask,
    timeout: datetime.timedelta,
) -> providers_pb2.SearchOffersResponse:
    try:
        return await provider.connection.offers.SearchOffers(
            providers_pb2.SearchOffersRequest(trip_offer_search_task=msg),
            timeout=timeout.total_seconds(),
        )
    except aio.AioRpcError:
        return providers_pb2.SearchOffersResponse()


class Repository(object):
    def __init__(self, producer: protocol.Producer, client: types.Client[bytes]):
        self._offer_search_set = client.set_("pending_offer_searches")
        self._producer = producer
        self._redis_client = client

    async def add_offer(
        self,
        identifier: str,
        offer: amqp_pb2.TripOfferSearchResult,
    ) -> None:
        await self._offers_list(identifier).push(
            protobuf.AnySerializer[amqp_pb2.TripOfferSearchResult].serialize(offer),
        )

    async def enqueue_trip_task(self, task: amqp_pb2.TripOfferSearchTask) -> str:
        await asyncio.gather(
            self._producer.publish(task, "offers.search.trip"),
            self._offer_search_set.add(task.offer_search_id),
        )

        return task.offer_search_id

    async def is_in_progress(self, identifier: str) -> bool:
        return await self._offer_search_set.has(identifier)

    async def mark_as_done(self, identifier: str) -> None:
        await self._offer_search_set.remove(identifier)

    async def pop_offers(self, identifier: str) -> list[amqp_pb2.TripOfferSearchResult]:
        return [
            protobuf.AnySerializer[amqp_pb2.TripOfferSearchResult].deserialize(offer)
            for offer in await self._offers_list(identifier).pop(
                await self._offers_list(identifier).length(),
            )
        ]

    def _offers_list(self, identifier: str) -> types.List[bytes]:
        return self._redis_client.list_("offers.{0}".format(identifier))
