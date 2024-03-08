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
        offer_segments: repository.OfferSegmentRepository,
        offers: repository.OfferRepository,
        offer_segment_details: repository.OfferSegmentDetailsRepository,
        default_page_size: int,
    ):
        self._search_results = search_results
        self._offer_segments = offer_segments
        self._offers = offers
        self._offer_segment_details = offer_segment_details
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_SearchResultServiceServicer_to_server(self, server)

    async def GetSearchResult(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetSearchResultRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetSearchResultResponse:
        search_result = await self._search_results.find_by_id(request.id)

        if not search_result:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetSearchResultResponse(search_result=search_result)

    async def GetOfferSegment(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferSegmentRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferSegmentResponse:
        offer_segment = await self._offer_segments.find_by_id(request.id)

        if not offer_segment:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferSegmentResponse(offer_segment=offer_segment)

    async def GetOffer(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferResponse:
        offer = await self._offers.find_by_id(request.id)

        if not offer:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferResponse(offer=offer)

    async def GetOfferSegmentDetails(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferSegmentDetailsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferSegmentDetailsResponse:
        offer_segment_details = await self._offer_segment_details.find_by_id(request.id)

        if not offer_segment_details:
            return await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferSegmentDetailsResponse(
            offer_segment_details=offer_segment_details,
        )
