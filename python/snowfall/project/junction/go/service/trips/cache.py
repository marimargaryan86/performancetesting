import contextlib
import datetime
from collections.abc import Sequence
from typing import Any

import pymongo
from pymongo import errors as pymongo_errors

from snowfall.project.junction.go.adapter import legs
from snowfall.project.junction.go.service.trips.v1alpha import trips_pb2
from snowfall.project.junction.go.v1 import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, resultset
from snowfall.stdlib.persistence.mongo import repository as mongo_repository
from snowfall.stdlib.persistence.redis import repository as redis_repository
from snowfall.stdlib.persistence.redis import types as redis


class LegCacheRepository(
    mongo_repository.ProtoRepository[trips_pb2.LegCache],
    mixins.FindByIdMixin[trips_pb2.LegCache],
    mixins.InsertManyMixin[trips_pb2.LegCache],
):
    _proto = trips_pb2.LegCache
    _indexes = (
        pymongo.IndexModel("expires_at", expireAfterSeconds=1, background=True),
    )
    _chunk_size = 100
    _ttl = datetime.timedelta(hours=1)

    def __init__(self, redis_client: redis.Client[bytes], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._redis = redis_client

    async def fetch_many(
        self,
        ids: Sequence[str],
        legs_adapter: legs.GrpcClient,
    ) -> None:
        if not await self._get_missing_ids(ids):
            return

        async with self._redis.lock("leg_cache_fetch_many:lock"):
            # Re-check for data in case another process has already fetched it
            missing_ids = list(await self._get_missing_ids(ids))
            if not missing_ids:
                return

            for start in range(0, len(missing_ids), self._chunk_size):
                chunk = missing_ids[start : start + self._chunk_size]
                legs_chunk = await legs_adapter.find_by_ids(
                    identifiers=chunk,
                    limit=self._chunk_size,
                )
                await self._insert_legs(legs_chunk.legs)

    async def find(
        self,
        ids: Sequence[str],
    ) -> resultset.ResultSet[trips_pb2.LegCache]:
        if not ids:
            raise ValueError("IDs can't be empty")

        return await self._find_with_cursor(
            filter_={
                mongo_repository.mongo_id_key: {
                    "$in": ids,
                },
            },
        )

    async def _insert_legs(self, leg_objects: Sequence[models_pb2.Leg]) -> None:
        with contextlib.suppress(pymongo_errors.BulkWriteError):
            await self.insert_many(
                [
                    trips_pb2.LegCache(
                        id=leg.id,
                        leg=leg,
                        expires_at=protobuf.datetime_to_protobuf(
                            datetime.datetime.now(tz=datetime.UTC) + self._ttl,
                        ),
                    )
                    for leg in leg_objects
                ],
                ordered=False,
            )

    async def _get_missing_ids(self, ids: Sequence[str]) -> set[str]:
        existing_ids = await self._find_existing_ids(ids)

        return set(ids) - set(existing_ids)

    async def _find_existing_ids(self, ids: Sequence[str]) -> list[str]:
        if not ids:
            return []

        return [
            leg_cache.id
            async for leg_cache in await self._execute(
                query=self._collection.find,
                filter={mongo_repository.mongo_id_key: {"$in": ids}},
                projection={mongo_repository.mongo_id_key: 1},
            )
        ]


class TripMetadata(redis_repository.RedisRecord):
    identifier: str
    duration: int
    is_multimodal: bool


class TripMetadataRepository(
    redis_repository.PydanticRepository[TripMetadata],
):
    _record_type: type[TripMetadata] = TripMetadata
    _ttl = datetime.timedelta(hours=1)
    _key_format = "trip_metadata:{0}"

    def __init__(
        self,
        client: redis.Client[bytes],
        leg_cache_repository: LegCacheRepository,
    ):
        super().__init__(client)
        self._leg_cache_repository = leg_cache_repository

    async def get_for_trip(
        self,
        trip_reference: models_pb2.TripReference,
    ) -> TripMetadata:
        metadata = await self.fetch(self._key_format.format(trip_reference.id))

        if metadata:
            return metadata

        leg_cache_objects = sorted(
            [
                leg_cache
                async for leg_cache in await self._leg_cache_repository.find(
                    ids=[
                        leg_id
                        for segment in trip_reference.segments
                        for leg_id in segment.leg_ids
                    ],
                )
            ],
            key=lambda leg_cache: protobuf.protobuf_to_datetime(
                leg_cache.leg.departure_at,
            ),
        )
        duration = protobuf.protobuf_to_datetime(
            leg_cache_objects[-1].leg.arrival_at,
        ) - protobuf.protobuf_to_datetime(
            leg_cache_objects[0].leg.departure_at,
        )
        is_multimodal = len({leg_cache.leg.type for leg_cache in leg_cache_objects}) > 1

        metadata = TripMetadata(
            identifier=trip_reference.id,
            duration=int(duration.total_seconds()),
            is_multimodal=is_multimodal,
        )

        await self.store(
            metadata,
            expires_at=datetime.datetime.now(datetime.UTC) + self._ttl,
            key=self._key_format.format(trip_reference.id),
        )

        return metadata
