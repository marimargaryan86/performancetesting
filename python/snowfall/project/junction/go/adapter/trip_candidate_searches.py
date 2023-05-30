import abc
import dataclasses
import datetime
from typing import Sequence

from snowfall.project.junction.go.adapter import errors
from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2, trips_pb2_grpc
from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.format import protobuf


@dataclasses.dataclass(frozen=True)
class TripCandidateSearchRequest(object):
    criteria: Sequence[trips_pb2.TripCandidateSearchCriteria]
    passengers: Sequence[offer_models_pb2.Passenger]
    allowed_segment_types: Sequence[models_pb2.Schedule.Type.ValueType]
    reseller_id: str
    currency_code: str | None
    pay_company_id: str | None
    session_token: str


class Client(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        trip_candidate_search: TripCandidateSearchRequest,
    ) -> trips_pb2.TripCandidateSearch:
        """Create a trip candidate search."""

    @abc.abstractmethod
    async def get(
        self,
        identifier: str,
    ) -> trips_pb2.TripCandidateSearch:
        """Get a trip candidate search."""


class DictClient(Client):
    def __init__(self) -> None:
        self._searches: dict[str, trips_pb2.TripCandidateSearch] = {}

    async def create(
        self,
        trip_candidate_search: TripCandidateSearchRequest,
    ) -> trips_pb2.TripCandidateSearch:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=1,
        )
        new_trip_candidate_search = trips_pb2.TripCandidateSearch(
            id=string.uuid(),
            expires_at=protobuf.datetime_to_protobuf(expires_at),
            criteria=trip_candidate_search.criteria,
            passengers=trip_candidate_search.passengers,
            allowed_segment_types=trip_candidate_search.allowed_segment_types,
        )
        self._searches[new_trip_candidate_search.id] = new_trip_candidate_search

        return new_trip_candidate_search

    async def get(self, identifier: str) -> trips_pb2.TripCandidateSearch:
        try:
            return self._searches[identifier]
        except KeyError as err:
            raise errors.NotFoundError() from err


class GrpcClient(Client):
    def __init__(
        self,
        trip_candidate_searches: trips_pb2_grpc.TripCandidateSearchServiceStub,
        timeout: int = 10,
    ) -> None:
        self._trip_candidate_searches = trip_candidate_searches
        self._timeout = timeout

    async def create(
        self,
        trip_candidate_search: TripCandidateSearchRequest,
    ) -> trips_pb2.TripCandidateSearch:
        response = await errors.handle_grpc_errors(
            self._trip_candidate_searches.EnqueueTripCandidateSearch(
                request=trips_pb2.EnqueueTripCandidateSearchRequest(
                    trip_candidate_search=_create_trip_candidate_search(
                        trip_candidate_search=trip_candidate_search,
                    ),
                ),
                timeout=self._timeout,
            ),
        )

        return response.trip_candidate_search

    async def get(
        self,
        identifier: str,
    ) -> trips_pb2.TripCandidateSearch:
        response = await errors.handle_grpc_errors(
            self._trip_candidate_searches.GetTripCandidateSearchDetails(
                request=trips_pb2.GetTripCandidateSearchDetailsRequest(
                    id=identifier,
                ),
                timeout=self._timeout,
            ),
        )

        return response.trip_candidate_search


def _create_trip_candidate_search(
    trip_candidate_search: TripCandidateSearchRequest,
) -> trips_pb2.TripCandidateSearch:
    search_proto = trips_pb2.TripCandidateSearch(
        passengers=trip_candidate_search.passengers,
        criteria=trip_candidate_search.criteria,
        allowed_segment_types=trip_candidate_search.allowed_segment_types,
        reseller_id=trip_candidate_search.reseller_id,
        session_token=trip_candidate_search.session_token,
    )

    if trip_candidate_search.currency_code:
        search_proto.currency_code = trip_candidate_search.currency_code

    if trip_candidate_search.pay_company_id:
        search_proto.pay_company_id = trip_candidate_search.pay_company_id

    return search_proto
