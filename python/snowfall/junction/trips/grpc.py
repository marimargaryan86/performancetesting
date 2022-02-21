import datetime

from grpc import aio

from snowfall.junction.trips import trips
from snowfall.junction.trips.v1alpha import amqp_pb2, trips_pb2, trips_pb2_grpc
from snowfall.transport import amqp
from snowfall.transport.grpc import Service

_TRIP_SEARCH_EXPIRY = datetime.timedelta(minutes=15)  # noqa: WPS432 - todo: config


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
