import datetime

import pymongo
from google.protobuf import timestamp_pb2
from motor import core

from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository
from snowfall.stdlib.v1 import amqp_pb2


class TripCandidateSearchRepository(
    repository.ProtoRepository[trips_pb2.TripCandidateSearch],
    mixins.InsertMixin[trips_pb2.TripCandidateSearch],
    mixins.FindByIdMixin[trips_pb2.TripCandidateSearch],
):
    _proto = trips_pb2.TripCandidateSearch
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )

    def __init__(
        self,
        collection: core.AgnosticCollection,
        ttl: datetime.timedelta,
    ) -> None:
        super().__init__(collection)

        self._ttl = ttl

    async def create(
        self,
        trip_candidate_search: trips_pb2.TripCandidateSearch,
    ) -> trips_pb2.TripCandidateSearch:
        new_trip_candidate_search = trips_pb2.TripCandidateSearch()
        expires_at = timestamp_pb2.Timestamp()
        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )

        new_trip_candidate_search.CopyFrom(trip_candidate_search)
        new_trip_candidate_search.id = string.uuid()
        new_trip_candidate_search.expires_at.CopyFrom(expires_at)
        new_trip_candidate_search.status = amqp_pb2.Trackable.STATUS_PENDING

        return await self.insert(new_trip_candidate_search)
