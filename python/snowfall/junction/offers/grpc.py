import grpc

from snowfall.junction.offers import amqp, offers
from snowfall.junction.offers.v1alpha import grpc_pb2, grpc_pb2_grpc, models_pb2
from snowfall.stdlib.transport.grpc import service


class OfferSearchService(service.Service, grpc_pb2_grpc.OfferSearchServiceServicer):
    def __init__(
        self,
        offers_searches: offers.OfferSearchRepository,
        publisher: amqp.OfferSearchProducer,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._offers_searches = offers_searches
        self._publisher = publisher

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["OfferSearchService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_OfferSearchServiceServicer_to_server(self, server)

    async def EnqueueOfferSearch(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.EnqueueOfferSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.EnqueueOfferSearchResponse:
        offer_search = await self._offers_searches.create(
            request.search,
        )
        await self._publisher.publish(offer_search)

        return grpc_pb2.EnqueueOfferSearchResponse(search=offer_search)

    async def GetOfferSearch(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferSearchResponse:
        offer_search = await self._offers_searches.find_by_id(request.id)

        if not offer_search:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferSearchResponse(search=offer_search)


class OfferService(service.Service, grpc_pb2_grpc.OfferServiceServicer):
    def __init__(
        self,
        offer_aggregates: offers.OfferAggregateMappingRepository,
        offer_results: offers.TripOfferRepository,
        default_page_size: int,
    ):
        self._aggregates = offer_aggregates
        self._offers_results = offer_results
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_OfferServiceServicer_to_server(self, server)

    async def GetOffer(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferResponse:
        offer_aggregate = await self._aggregates.find_by_id(request.id)

        if not offer_aggregate:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        offer_results = await self._offers_results.find(
            ids=list(offer_aggregate.offer_result_ids),  # type: ignore[union-attr]
            cursor="",
        )

        return grpc_pb2.GetOfferResponse(
            offer=models_pb2.OfferAggregate(
                id=offer_aggregate.id,  # type: ignore[union-attr]
                expires_at=offer_aggregate.expires_at,  # type: ignore[union-attr]
                groups=[offer_result async for offer_result in offer_results],
            ),
        )

    async def ListOffers(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListOffersRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListOffersResponse:
        if not request.offer_search_id:
            # TODO: if request.payload.offer_ids.ids:
            return grpc_pb2.ListOffersResponse()

        offer_aggregates = await self._aggregates.find_by_offer_search_id(
            request.offer_search_id,
            cursor=request.page_token,
        )

        offer_aggregates.limit(
            request.page_size
            if request.page_size is not None
            else self._default_page_size,
        )

        offer_list = []

        async for aggregate in offer_aggregates:
            offer_results = await self._offers_results.find(
                ids=list(aggregate.offer_result_ids),
                cursor="",
            )
            offer_list.append(
                models_pb2.OfferAggregate(
                    id=aggregate.id,
                    expires_at=aggregate.expires_at,
                    groups=[offer_result async for offer_result in offer_results],
                ),
            )

        return grpc_pb2.ListOffersResponse(
            offers=offer_list,
            next_page_token=await offer_aggregates.cursor(),
        )
