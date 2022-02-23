import grpc

from snowfall.junction.offers.offers import OfferSearchRepository
from snowfall.junction.offers.v1alpha import offers_pb2, offers_pb2_grpc
from snowfall.transport.grpc import Service


class OfferService(Service, offers_pb2_grpc.OfferServiceServicer):
    def __init__(self, offers_searches: OfferSearchRepository, default_page_size: int):
        self._default_page_size = default_page_size
        self._offers_searches = offers_searches

    def get_name(self) -> str:
        return offers_pb2.DESCRIPTOR.services_by_name["OfferService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        offers_pb2_grpc.add_OfferServiceServicer_to_server(self, server)

    async def EnqueueOfferSearch(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.EnqueueOfferSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> offers_pb2.EnqueueOfferSearchResponse:
        offer_search = await self._offers_searches.create(
            request.search,
        )

        # todo: publish search to queue

        return offers_pb2.EnqueueOfferSearchResponse(search=offer_search)

    async def GetOfferSearch(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.GetOfferSearchRequest,
        context: grpc.aio.ServicerContext,
    ) -> offers_pb2.GetOfferSearchResponse:
        offer_search = await self._offers_searches.find_by_id(request.id)

        if not offer_search:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return offers_pb2.GetOfferSearchResponse(search=offer_search)

    async def ListOffers(  # type: ignore[override] # noqa: N802
        self,
        request: offers_pb2.ListOffersRequest,
        context: grpc.aio.ServicerContext,
    ) -> offers_pb2.ListOffersResponse:
        # todo: get offer results from persistence
        return offers_pb2.ListOffersResponse()
