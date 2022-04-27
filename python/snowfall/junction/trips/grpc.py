from grpc import StatusCode, aio

from snowfall.junction.trips import trips
from snowfall.junction.trips.v1alpha import amqp_pb2, trips_pb2, trips_pb2_grpc
from snowfall.stdlib.transport import amqp
from snowfall.stdlib.transport.grpc import Service


class TripService(Service, trips_pb2_grpc.TripServiceServicer):
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
            await context.abort(StatusCode.NOT_FOUND)

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
            request.page_size
            if request.page_size is not None
            else self._default_page_size,
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
            await context.abort(StatusCode.NOT_FOUND)

        return trips_pb2.GetSegmentResponse(segment=segment)


class TripSearchService(Service, trips_pb2_grpc.TripSearchServiceServicer):
    def __init__(
        self,
        repository: trips.TripSearchRepository,
        producer: amqp.Producer,
    ) -> None:
        self._producer = producer
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
            await context.abort(StatusCode.NOT_FOUND)

        return trips_pb2.GetTripSearchDetailsResponse(trip_search=trip_search)
