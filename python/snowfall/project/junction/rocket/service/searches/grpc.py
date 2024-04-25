import asyncio
import typing

import grpc

from snowfall.project.junction.rocket.service.searches import amqp, repository
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
)
from snowfall.stdlib.transport.grpc import service


class SearchService(service.Service, grpc_pb2_grpc.SearchServiceServicer):
    def __init__(
        self,
        searches_repo: repository.SearchRepository,
        publisher: amqp.SearchProducer,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._searches_repo = searches_repo
        self._publisher = publisher

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["SearchService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_SearchServiceServicer_to_server(self, server)

    async def EnqueueSearch(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.EnqueueSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.EnqueueSearchResponse:
        search = await self._searches_repo.create(
            request.search,
        )
        await self._publisher.publish(search)

        return grpc_pb2.EnqueueSearchResponse(search=search)

    async def GetSearch(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetSearchResponse:
        search = await self._searches_repo.find_by_id(request.id)

        if not search:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetSearchResponse(search=search)


class SearchResultService(service.Service, grpc_pb2_grpc.SearchResultServiceServicer):
    _sort_mapping: typing.ClassVar = {
        "id": "_id",
        "created_at": "created_at",
    }

    def __init__(
        self,
        search_results: repository.SearchResultRepository,
        searches: repository.SearchRepository,
        offers: repository.OfferRepository,
        default_page_size: int,
    ):
        self._search_results = search_results
        self._searches = searches
        self._offers = offers
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["SearchResultService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_SearchResultServiceServicer_to_server(self, server)

    async def ListSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListSearchResultsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListSearchResultsResponse:
        search = await self._searches.find_by_id(request.search_id)
        if search is not None:
            response = await asyncio.gather(
                *[
                    self._search_results.find_by_id(search_result_id)
                    for search_result_id in search.search_result_ids
                ],
            )

            search_results = [result for result in response if result]

            return grpc_pb2.ListSearchResultsResponse(
                search_results=search_results,
            )

        return await context.abort(grpc.StatusCode.NOT_FOUND)


class QuoteService(service.Service, grpc_pb2_grpc.QuoteServiceServicer):
    def __init__(
        self,
        quotes_repo: repository.QuoteRepository,
        publisher: amqp.QuoteTaskProducer,
    ):
        self._quotes_repo = quotes_repo
        self._publisher = publisher

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["QuoteService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_QuoteServiceServicer_to_server(self, server)

    async def CreateQuote(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreateQuoteRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreateQuoteResponse:
        quote = await self._quotes_repo.create(
            request.offer_ids,
        )
        await self._publisher.publish(quote, request.reseller_id)

        return grpc_pb2.CreateQuoteResponse(quote=quote)

    async def GetQuote(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetQuoteRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetQuoteResponse:
        quote = await self._quotes_repo.find_by_id(request.id)

        if not quote:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetQuoteResponse(quote=quote)
