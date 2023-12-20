import asyncio

from grpc import aio

from snowfall.project.junction.service.gateway.v1 import trips_pb2, trips_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.service import tasks
from snowfall.stdlib.transport.amqp import protocol
from snowfall.stdlib.transport.grpc import service


class Service(service.Service, trips_pb2_grpc.TripServiceServicer):
    def __init__(
        self,
        producer: protocol.Producer,
        runner: tasks.Runner[trips_pb2.TripSearchResult],
    ):
        self._producer = producer
        self._runner = runner

    def get_name(self) -> str:
        return trips_pb2.DESCRIPTOR.services_by_name["TripService"].full_name

    def register(self, server: aio.Server) -> None:
        trips_pb2_grpc.add_TripServiceServicer_to_server(self, server)

    async def EnqueueTripSearch(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.EnqueueTripSearchRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.EnqueueTripSearchResponse:
        trip_search_id = string.uuid()
        search_mode = request.WhichOneof("search_mode")

        await asyncio.gather(
            self._producer.publish(
                trips_pb2.TripSearchTask(
                    id=trip_search_id,
                    one_way=request.one_way if search_mode == "one_way" else None,
                    round_trip=request.round_trip
                    if search_mode == "round_trip"
                    else None,
                    multi_city=request.multi_city
                    if search_mode == "multi_city"
                    else None,
                    passengers=request.passengers,
                ),
                "tasks.trip_search",
            ),
            self._runner.mark_as_in_progress(trip_search_id),
        )

        return trips_pb2.EnqueueTripSearchResponse(id=trip_search_id)

    async def DrainTripSearchResults(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.DrainTripSearchResultsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.DrainTripSearchResultsResponse:
        return trips_pb2.DrainTripSearchResultsResponse(
            is_in_progress=await self._runner.is_in_progress(request.id),
            results=await self._runner.drain_results(request.id),
        )
