import datetime
import uuid

import pymongo
from google.protobuf import timestamp_pb2
from motor import motor_asyncio

from snowfall.junction.trips.v1alpha import trips_pb2
from snowfall.persistence.mongo import repository


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
