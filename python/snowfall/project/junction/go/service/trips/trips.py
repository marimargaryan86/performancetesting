import contextlib
import datetime
from collections.abc import Sequence

import pymongo
from google.protobuf import timestamp_pb2
from motor import core
from pymongo import errors as pymongo_errors

from snowfall.project.junction.go.service.planner.v1 import planner_pb2
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset
from snowfall.stdlib.v1 import amqp_pb2


class SegmentRepository(repository.ProtoRepository[models_pb2.SegmentReference]):
    _proto = models_pb2.SegmentReference
    _nested_path = "segments"
    _indexes = (pymongo.IndexModel("segments._id", background=True),)

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.SegmentReference]:
        filter_ = (
            {
                "segments._id": {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            filter_=filter_,
            cur=cursor,
        )

    async def find_by_id(
        self,
        document_id: str,
    ) -> models_pb2.SegmentReference | None:
        segments = await self._find_with_cursor(
            filter_={
                "segments._id": {
                    "$eq": document_id,
                },
            },
        )

        try:
            return await segments.take()
        except StopAsyncIteration:
            return None


class TripRepository(
    repository.ProtoRepository[models_pb2.TripReference],
    mixins.FindByIdMixin[models_pb2.TripReference],
):
    _proto = models_pb2.TripReference

    async def add_multiple_if_missing(
        self,
        trips: Sequence[models_pb2.TripReference],
    ) -> None:
        trips_ids = set({trip.id for trip in trips})
        existing_trips = await self._execute(
            self._collection.find,
            filter={
                repository.mongo_id_key: {
                    "$in": list(trips_ids),
                },
            },
            projection={
                repository.mongo_id_key: True,
            },
        )

        missing_ids = trips_ids - set(
            {existing.id async for existing in existing_trips},
        )

        if missing_ids:
            with contextlib.suppress(pymongo_errors.BulkWriteError):
                await self._execute(
                    self._collection.insert_many,
                    documents=[
                        self._coder.encode(trip)
                        for trip in trips
                        if trip.id in missing_ids
                    ],
                    ordered=False,
                )

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.TripReference]:
        filter_ = (
            {
                repository.mongo_id_key: {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )


class TripSearchRepository(  # noqa: WPS215
    repository.ProtoRepository[trips_pb2.TripSearch],
    mixins.FindByIdMixin[trips_pb2.TripSearch],
    mixins.InsertMixin[trips_pb2.TripSearch],
    mixins.StatusMixin[trips_pb2.TripSearch],
):
    _proto = trips_pb2.TripSearch
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

    async def add_results_from_journey_search(
        self,
        trip_search: trips_pb2.TripSearch,
        response: planner_pb2.SearchJourneyResponse,
    ) -> trips_pb2.TripSearch:
        new_trip_search = trips_pb2.TripSearch()

        new_trip_search.CopyFrom(trip_search)
        new_trip_search.ClearField("trip_ids")
        new_trip_search.trip_ids.extend([trip.id for trip in response.trips])
        # TODO: can't assume this once journey planner call isn't blocking
        new_trip_search.status = amqp_pb2.Trackable.STATUS_COMPLETED

        update = await self._execute(
            self._collection.update_one,
            {"_id": new_trip_search.id},
            {
                "$set": {
                    "trip_ids": list(new_trip_search.trip_ids),
                    "status": new_trip_search.status,
                },
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return new_trip_search

    async def insert(self, trip_search: trips_pb2.TripSearch) -> trips_pb2.TripSearch:
        new_trip_search = trips_pb2.TripSearch()

        new_trip_search.CopyFrom(trip_search)

        new_trip_search.id = string.uuid()
        new_trip_search.status = amqp_pb2.Trackable.STATUS_PENDING
        expires_at = timestamp_pb2.Timestamp()

        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
        )
        new_trip_search.expires_at.CopyFrom(expires_at)

        return await super().insert(new_trip_search)


class TripCandidateSearchRepository(  # noqa: WPS215
    repository.ProtoRepository[trips_pb2.TripCandidateSearch],
    mixins.FindByIdMixin[trips_pb2.TripCandidateSearch],
    mixins.InsertMixin[trips_pb2.TripCandidateSearch],
    mixins.StatusMixin[trips_pb2.TripCandidateSearch],
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

    async def add_offer_search_ids(
        self,
        trip_candidate_search_id: str,
        offer_search_ids: Sequence[str],
    ) -> bool:
        update = await self._execute(
            self._collection.update_one,
            {"_id": trip_candidate_search_id},
            {
                "$set": {
                    "offer_search_ids": list(offer_search_ids),
                },
            },
        )

        return bool(update.acknowledged)
