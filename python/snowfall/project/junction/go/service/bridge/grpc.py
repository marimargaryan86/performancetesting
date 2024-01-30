from grpc import StatusCode, aio

from snowfall.project.junction.go.service.bridge import trip_candidates
from snowfall.project.junction.go.service.bridge.v1alpha import (
    amqp_pb2,
    trips_pb2,
    trips_pb2_grpc,
)
from snowfall.stdlib.transport.amqp import producer
from snowfall.stdlib.transport.grpc import service


class TripCandidateSearchService(
    service.Service,
    trips_pb2_grpc.TripCandidateSearchServiceServicer,
):
    def __init__(
        self,
        producer_obj: producer.Producer,
        repository: trip_candidates.TripCandidateSearchRepository,
    ):
        self._producer_obj = producer_obj
        self._repository = repository

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
        search = await self._repository.create(
            trip_candidate_search=request.trip_candidate_search,
        )

        await self._producer_obj.publish(
            amqp_pb2.TripCandidateSearchTask(
                trip_candidate_search=search,
            ),
            "bridge.trip_candidates.search",
        )

        return trips_pb2.EnqueueTripCandidateSearchResponse(
            trip_candidate_search=search,
        )

    async def GetTripCandidateSearchDetails(  # type: ignore[override] # noqa: N802
        self,
        request: trips_pb2.GetTripCandidateSearchDetailsRequest,
        context: aio.ServicerContext,
    ) -> trips_pb2.GetTripCandidateSearchDetailsResponse:
        return await context.abort(StatusCode.NOT_IMPLEMENTED)
