import asyncio
import typing
from collections.abc import Sequence

import grpc

from snowfall.project.junction.rocket.service.searches import amqp, repository
from snowfall.project.junction.rocket.service.searches.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
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


class OfferService(service.Service, grpc_pb2_grpc.OfferServiceServicer):
    def __init__(
        self,
        offers_repo: repository.OfferRepository,
    ):
        self._offers_repo = offers_repo

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_OfferServiceServicer_to_server(self, server)

    async def GetOffer(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferResponse:
        offer = await self._offers_repo.find_by_id(request.id)

        if not offer:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferResponse(offer=offer)


class QuoteService(service.Service, grpc_pb2_grpc.QuoteServiceServicer):
    def __init__(
        self,
        quotes_repo: repository.QuoteRepository,
        offers_repo: repository.OfferRepository,
        publisher: amqp.QuoteTaskProducer,
    ):
        self._quotes_repo = quotes_repo
        self._offers_repo = offers_repo
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
        offers_result = await self._offers_repo.find(
            ids=list(request.offer_ids),
            cursor="",
        )
        offers = [offer async for offer in offers_result]

        if not offers or len(offers) < len(request.offer_ids):
            return await context.abort(
                code=grpc.StatusCode.NOT_FOUND,
                details="No offers found for the provided offer ids {0}".format(
                    list(set(request.offer_ids) - {offer.id for offer in offers}),
                ),
            )

        vertical_type = self._get_vertical_type(offers)

        if vertical_type == models_pb2.VERTICAL_TYPE_UNSPECIFIED:
            return await context.abort(
                code=grpc.StatusCode.FAILED_PRECONDITION,
                details="Invalid vertical types found",
            )

        quote = await self._quotes_repo.create(
            offer_ids=request.offer_ids,
            reseller_id=request.reseller_id,
            reseller_pay_company_id=request.reseller_pay_company_id,
            reseller_currency=request.reseller_currency,
            vertical_type=vertical_type,
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

    def _get_vertical_type(
        self,
        offers: Sequence[models_pb2.Offer],
    ) -> models_pb2.VerticalType.ValueType:
        offer_verticals: set[models_pb2.VerticalType.ValueType] = set()
        for offer in offers:
            if offer.HasField("rail"):
                offer_verticals.add(models_pb2.VERTICAL_TYPE_RAIL)
            elif offer.HasField("car_rental"):
                offer_verticals.add(models_pb2.VERTICAL_TYPE_CAR)
            elif offer.HasField("ferry"):
                offer_verticals.add(models_pb2.VERTICAL_TYPE_FERRY)

        if not offer_verticals or len(offer_verticals) > 1:
            return models_pb2.VERTICAL_TYPE_UNSPECIFIED

        return offer_verticals.pop()
