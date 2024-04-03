import abc
import dataclasses
from collections.abc import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.v1 import sort_pb2


@dataclasses.dataclass(frozen=True)
class ListTripCandidatesFilter:
    identifier: str
    limit: int | None = None
    cursor: str | None = None
    sort_by: sort_pb2.Sort | None = None
    cabin_classes: Sequence[models_pb2.CabinClass.Type.ValueType] | None = None


class Client(abc.ABC):
    @abc.abstractmethod
    async def list_trip_candidates_by_trip_candidate_search(
        self,
        filter_: ListTripCandidatesFilter,
    ) -> trips_pb2.ListTripCandidatesResponse:
        """Get offer results for an offer search."""


class DictClient(Client):
    async def list_trip_candidates_by_trip_candidate_search(
        self,
        filter_: ListTripCandidatesFilter,
    ) -> trips_pb2.ListTripCandidatesResponse:
        return trips_pb2.ListTripCandidatesResponse()


class GrpcClient(Client):
    def __init__(
        self,
        trip_candidates: trips_pb2_grpc.TripCandidateServiceStub,
        timeout: int = 10,
    ):
        self._trip_candidates = trip_candidates
        self._timeout = timeout

    async def list_trip_candidates_by_trip_candidate_search(
        self,
        filter_: ListTripCandidatesFilter,
    ) -> trips_pb2.ListTripCandidatesResponse:
        request = trips_pb2.ListTripCandidatesRequest(
            page_token=filter_.cursor or "",
            trip_candidate_search_id=filter_.identifier,
            cabin_class_types=filter_.cabin_classes,
            sort_by=filter_.sort_by,
        )

        if filter_.limit is not None:
            request.page_size = filter_.limit

        return await errors.handle_grpc_errors(
            self._trip_candidates.ListTripCandidates(
                request=request,
                timeout=self._timeout,
            ),
        )
