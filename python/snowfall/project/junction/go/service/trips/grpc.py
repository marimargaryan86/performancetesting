from collections.abc import Sequence

from grpc import StatusCode, aio

from snowfall.project.junction.go.adapter import offer_searches, offers
from snowfall.project.junction.go.service.trips import trips
from snowfall.project.junction.go.service.trips.v1alpha import (
    amqp_pb2,
    trips_pb2,
    trips_pb2_grpc,
)
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import service
from snowfall.stdlib.v1 import amqp_pb2 as std_amqp_pb2


class TripService(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        segments: trips.SegmentRepository,
        trips_repository: trips.TripRepository,
        default_page_size: int,
    ):
        self._default_page_size = default_page_size
        self._segments = segments
        self._trips = trips_repository

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def GetTrip(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.GetTripRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.GetTripResponse:
        trip = await self._trips.find_by_id(request.id)

        if not trip:
            return await context.abort(StatusCode.NOT_FOUND)

        return trips_pb2.GetTripResponse(trip=trip)

    async def ListTrips(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.ListTripsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.ListTripsResponse:
        trips_result = await self._trips.find(
            ids=list(request.ids),
            cursor=request.page_token,
        )

        trips_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return trips_pb2.ListTripsResponse(
            trips=[trip async for trip in trips_result],
            next_page_token=await trips_result.cursor(),
        )

    async def GetSegment(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.GetSegmentRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.GetSegmentResponse:
        segment = await self._segments.find_by_id(request.id)

        if segment is None:
            return await context.abort(StatusCode.NOT_FOUND)

        return trips_pb2.GetSegmentResponse(segment=segment)

    async def ListSegments(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.ListSegmentsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.ListSegmentsResponse:
        segments_result = await self._segments.find(
            ids=list(request.ids),
            cursor=request.page_token,
        )

        segments_result.limit(
            request.page_size if request.page_size else self._default_page_size,
        )

        return trips_pb2.ListSegmentsResponse(
            segments=[segment async for segment in segments_result],
            next_page_token=await segments_result.cursor(),
        )


class TripSearchService(service.Service, trips_pb2_grpc.TripSearchServiceServicer):
    def __init__(
        self,
        repository: trips.TripSearchRepository,
        producer_obj: producer.Producer,
    ) -> None:
        self._producer = producer_obj
        self._repository = repository

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripSearchService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripSearchServiceServicer_to_server(self, server)

    async def EnqueueTripSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripSearchResponse:
        trip_search = await self._repository.insert(request.trip_search)
        await self._producer.publish(
            amqp_pb2.TripSearchTask(
                trip_search=trip_search,
            ),
            "trips.search",
        )

        return trips_pb2.EnqueueTripSearchResponse(
            trip_search=trip_search,
        )

    async def GetTripSearchDetails(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.GetTripSearchDetailsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.GetTripSearchDetailsResponse:
        trip_search = await self._repository.find_by_id(request.id)

        if not trip_search:
            return await context.abort(StatusCode.NOT_FOUND)

        return trips_pb2.GetTripSearchDetailsResponse(trip_search=trip_search)


_FINAL_STATUSES = frozenset(
    (
        std_amqp_pb2.Trackable.Status.STATUS_COMPLETED,
        std_amqp_pb2.Trackable.Status.STATUS_FAILED,
    ),
)


def status_from_statuses(
    statuses: Sequence[std_amqp_pb2.Trackable.Status.ValueType],
) -> std_amqp_pb2.Trackable.Status.ValueType:
    statuses_set = set(statuses)

    if statuses_set and all(status in _FINAL_STATUSES for status in statuses_set):
        if std_amqp_pb2.Trackable.Status.STATUS_COMPLETED in statuses_set:
            return std_amqp_pb2.Trackable.Status.STATUS_COMPLETED

        return std_amqp_pb2.Trackable.Status.STATUS_FAILED

    if std_amqp_pb2.Trackable.Status.STATUS_PROCESSING in statuses_set:
        return std_amqp_pb2.Trackable.Status.STATUS_PROCESSING

    return std_amqp_pb2.Trackable.Status.STATUS_PENDING


class TripCandidateSearchService(
    service.Service,
    trips_pb2_grpc.TripCandidateSearchServiceServicer,
):
    def __init__(
        self,
        repository: trips.TripCandidateSearchRepository,
        producer_obj: producer.Producer,
        offer_search_adapter: offer_searches.Client,
        default_page_size: int,
    ):
        self._repository = repository
        self._offer_search_adapter = offer_search_adapter
        self._producer = producer_obj
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name[
            "TripCandidateSearchService"
        ].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripCandidateSearchServiceServicer_to_server(self, server)

    async def EnqueueTripCandidateSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripCandidateSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripCandidateSearchResponse:
        trip_candidate_search = await self._repository.create(
            request.trip_candidate_search,
        )

        await self._producer.publish(
            amqp_pb2.TripCandidateSearchTask(
                trip_candidate_search=trip_candidate_search,
            ),
            "trip_candidates.search",
        )

        return trips_pb2.EnqueueTripCandidateSearchResponse(
            trip_candidate_search=trip_candidate_search,
        )

    async def GetTripCandidateSearchDetails(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.GetTripCandidateSearchDetailsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.GetTripCandidateSearchDetailsResponse:
        trip_candidate_search = await self._repository.find_by_id(request.id)

        if not trip_candidate_search:
            return await context.abort(StatusCode.NOT_FOUND)

        offer_search_ids = trip_candidate_search.offer_search_ids

        if trip_candidate_search.status not in _FINAL_STATUSES and offer_search_ids:
            statuses: list[std_amqp_pb2.Trackable.Status.ValueType] = []
            cursor = ""

            while True:
                offer_searches_response = await self._offer_search_adapter.find_by_ids(
                    offer_search_ids,
                    limit=self._default_page_size,
                    cursor=cursor,
                )

                statuses.extend(
                    offer_search.status
                    for offer_search in offer_searches_response.offer_searches
                )
                cursor = offer_searches_response.next_page_token

                if not offer_searches_response.offer_searches:
                    break

            trip_candidate_search.status = status_from_statuses(
                statuses=statuses,
            )

        return trips_pb2.GetTripCandidateSearchDetailsResponse(
            trip_candidate_search=trip_candidate_search,
        )


class TripCandidateService(
    service.Service,
    trips_pb2_grpc.TripCandidateServiceServicer,
):
    def __init__(
        self,
        offers_adapter: offers.GrpcClient,
        repository: trips.TripCandidateSearchRepository,
        default_page_size: int,
    ):
        self._offers_adapter = offers_adapter
        self._repository = repository
        self._default_page_size = default_page_size

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripCandidateService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripCandidateServiceServicer_to_server(self, server)

    async def ListTripCandidates(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.ListTripCandidatesRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.ListTripCandidatesResponse:
        trip_candidate_search = await self._repository.find_by_id(
            request.trip_candidate_search_id,
        )

        if not trip_candidate_search:
            return await context.abort(StatusCode.NOT_FOUND)

        offer_search_ids = trip_candidate_search.offer_search_ids

        if not offer_search_ids:
            return trips_pb2.ListTripCandidatesResponse(
                next_page_token="",
            )

        offer_aggregates = await self._offers_adapter.find_offers_by_offer_searches(
            offers.FindOffersByOfferSearchesFilter(
                identifiers=offer_search_ids,
                limit=request.page_size,
                cursor=request.page_token,
                sort_by=request.sort_by,
                cabin_classes=request.cabin_class_types,
            ),
        )

        return trips_pb2.ListTripCandidatesResponse(
            offers=offer_aggregates.offers,
            next_page_token=offer_aggregates.next_page_token,
        )
