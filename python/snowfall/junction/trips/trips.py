import datetime
import uuid

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.common.v1alpha import models_pb2
from snowfall.junction.planner.v1alpha import planner_pb2
from snowfall.junction.trips.v1alpha import trips_pb2
from snowfall.persistence.mongo import repository, resultset


class TripRepository(repository.ProtoRepository[models_pb2.TripReference]):
    _proto = models_pb2.TripReference

    async def add_from_journey_search(
        self,
        response: planner_pb2.SearchJourneyResponse,
    ) -> None:
        trips_ids = set({trip.id for trip in response.trips})
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
            await self._execute(
                self._collection.insert_many,
                documents=[
                    self._coder.encode(trip)
                    for trip in response.trips
                    if trip.id in missing_ids
                ],
            )

    async def find(
        self,
        ids: list[str],
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


class TripSearchRepository(repository.ProtoRepository[trips_pb2.TripSearch]):
    _proto = trips_pb2.TripSearch
    _indexes = [pymongo.IndexModel("expires_at", expireAfterSeconds=1)]

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
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

        update = await self._execute(
            self._collection.update_one,
            {"_id": new_trip_search.id},
            {
                "$set": {"trip_ids": list(new_trip_search.trip_ids)},
            },
        )

        if not update.acknowledged:
            raise RuntimeError()

        return new_trip_search

    async def insert(self, message: trips_pb2.TripSearch) -> trips_pb2.TripSearch:
        document = trips_pb2.TripSearch()

        document.CopyFrom(message)

        document.id = str(uuid.uuid4())
        expires_at = timestamp_pb2.Timestamp()

        expires_at.FromDatetime(
            datetime.datetime.now(tz=datetime.timezone.utc) + self._ttl,
        )
        document.expires_at.CopyFrom(expires_at)

        return await super().insert(document)
