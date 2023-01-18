import grpc

from snowfall.project.junction.service.offers import amqp, offers, price_quotes
from snowfall.project.junction.service.offers.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
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


class OfferService(service.Service, grpc_pb2_grpc.OfferServiceServicer):  # noqa: WPS214
    def __init__(  # noqa: WPS211
        self,
        offer_aggregates: offers.OfferAggregateMappingRepository,
        offer_results: offers.TripOfferRepository,
        offer_group_details: offers.TripOfferGroupDetailsRepository,
        offer_options: offers.OfferOptionsRepository,
        offer_option_details: offers.OfferOptionDetailsRepository,
        default_page_size: int,
    ):
        self._aggregates = offer_aggregates
        self._offers_results = offer_results
        self._group_details = offer_group_details
        self._options = offer_options
        self._option_details = offer_option_details
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
        payload_attr_name = request.WhichOneof("payload")
        if payload_attr_name == "offer_search_id":
            offer_aggregates = await self._aggregates.find_by_offer_search_ids(
                [request.offer_search_id],
                cursor=request.page_token,
                cabin_classes=list(request.cabin_class_types),
            )
        elif payload_attr_name == "offer_ids":
            offer_aggregates = await self._aggregates.find(
                list(request.offer_ids.ids),
                cursor=request.page_token,
            )
        else:
            offer_aggregates = await self._aggregates.find_by_offer_search_ids(
                list(request.offer_search_ids.ids),
                cursor=request.page_token,
                cabin_classes=list(request.cabin_class_types),
            )

        offer_aggregates.limit(
            request.page_size if request.page_size else self._default_page_size,
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

    async def GetOfferGroup(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferGroupRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferGroupResponse:
        offer_group = await self._offers_results.find_by_id(request.id)

        if not offer_group:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferGroupResponse(group=offer_group)

    async def ListOfferGroups(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListOfferGroupsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListOfferGroupsResponse:
        offer_groups = await self._offers_results.find(
            list(request.offer_group_ids.ids),
            cursor=request.page_token,
        )

        return grpc_pb2.ListOfferGroupsResponse(
            groups=[offer_group async for offer_group in offer_groups],
            next_page_token=await offer_groups.cursor(),
        )

    async def GetOfferGroupDetails(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferGroupDetailsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferGroupDetailsResponse:
        details = await self._group_details.find_by_id(request.id)

        if not details:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferGroupDetailsResponse(details=details)

    async def ListOfferGroupDetails(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListOfferGroupDetailsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListOfferGroupDetailsResponse:
        details = await self._group_details.find(
            list(request.offer_group_details_ids.ids),
            cursor=request.page_token,
        )

        return grpc_pb2.ListOfferGroupDetailsResponse(
            details=[detail async for detail in details],
            next_page_token=await details.cursor(),
        )

    async def GetOfferOption(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferOptionRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferOptionResponse:
        option = await self._options.find_by_id(request.id)

        if not option:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferOptionResponse(option=option)

    async def ListOfferOptions(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListOfferOptionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListOfferOptionsResponse:
        options = await self._options.find(
            list(request.offer_option_ids.ids),
            cursor=request.page_token,
        )

        return grpc_pb2.ListOfferOptionsResponse(
            options=[option async for option in options],
            next_page_token=await options.cursor(),
        )

    async def GetOfferOptionDetails(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetOfferOptionDetailsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetOfferOptionDetailsResponse:
        details = await self._option_details.find_by_id(request.id)

        if not details:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetOfferOptionDetailsResponse(details=details)

    async def ListOfferOptionDetails(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.ListOfferOptionDetailsRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.ListOfferOptionDetailsResponse:
        details = await self._option_details.find(
            list(request.offer_option_details_ids.ids),
            cursor=request.page_token,
        )

        return grpc_pb2.ListOfferOptionDetailsResponse(
            details=[detail async for detail in details],
            next_page_token=await details.cursor(),
        )


class PriceQuoteService(service.Service, grpc_pb2_grpc.PriceQuoteServiceServicer):
    def __init__(
        self,
        price_quotes_repository: price_quotes.PriceQuoteContainerRepository,
        publisher: amqp.PriceQuoteProducer,
    ):
        self._price_quotes = price_quotes_repository
        self._publisher = publisher

    def get_name(self) -> str:
        return grpc_pb2.DESCRIPTOR.services_by_name["PriceQuoteService"].full_name

    def register(self, server: grpc.aio.Server) -> None:
        grpc_pb2_grpc.add_PriceQuoteServiceServicer_to_server(self, server)

    async def CreatePriceQuote(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.CreatePriceQuoteRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.CreatePriceQuoteResponse:
        price_quote = await self._price_quotes.create(
            offer_id=request.offer_id,
            option_ids=list(request.option_ids),
            session_token=request.session_token,
        )
        await self._publisher.publish(price_quote)

        return grpc_pb2.CreatePriceQuoteResponse(price_quote=price_quote)

    async def GetPriceQuote(  # type: ignore[override] # noqa: N802
        self,
        request: grpc_pb2.GetPriceQuoteRequest,
        context: grpc.aio.ServicerContext,
    ) -> grpc_pb2.GetPriceQuoteResponse:
        price_quote = await self._price_quotes.find_by_id(request.id)

        if not price_quote:
            await context.abort(grpc.StatusCode.NOT_FOUND)

        return grpc_pb2.GetPriceQuoteResponse(price_quote=price_quote)
