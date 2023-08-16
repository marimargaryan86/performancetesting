import asyncio
import dataclasses
import logging
import uuid
from collections.abc import Iterable, Sequence
from typing import Any

from pymongo import GEOSPHERE, IndexModel, results

from snowfall.project.junction.go.service.places.v1 import models_pb2
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib import string
from snowfall.stdlib.persistence.mongo import mixins, normalizers, repository, resultset

_mongo_id_key = "_id"
_proto_id_key = "id"
_location_key = "location"

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


@dataclasses.dataclass(frozen=True)
class PlaceTypeDistancePair(object):
    max_distance_meters: int
    location_type: models_pb2.Location.Type.ValueType


@dataclasses.dataclass(frozen=True)
class FindPlacesPerAreaFilter(object):
    latitude: float
    longitude: float
    type_distances: Sequence[PlaceTypeDistancePair]


def _unique(locations: Sequence[models_pb2.Location]) -> Sequence[models_pb2.Location]:
    unique_locations = []
    found_ids = set()

    for location in locations:
        if location.id not in found_ids:
            unique_locations.append(location)
            found_ids.add(location.id)

    return unique_locations


class LocationRepository(
    mixins.FindByIdMixin[models_pb2.Location],
    repository.ProtoRepository[models_pb2.Location],
):
    _indexes = (IndexModel([("coordinates", GEOSPHERE)], background=True),)
    _proto = models_pb2.Location

    async def find(
        self,
        cursor: str,
        identifiers: Sequence[str] | None = None,
    ) -> resultset.ResultSet[models_pb2.Location]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={_mongo_id_key: {"$in": identifiers}} if identifiers else None,
        )

    async def find_within_area(
        self,
        cursor: str,
        latitude: float,
        longitude: float,
        max_distance_meters: int,
    ) -> resultset.ResultSet[models_pb2.Location]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={
                "coordinates": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": max_distance_meters,
                    },
                },
            },
        )

    async def find_within_area_per_type(
        self,
        cursor: str,
        filter_: FindPlacesPerAreaFilter,
    ) -> Sequence[models_pb2.Location]:
        locations = []

        for type_distance_pair in filter_.type_distances:
            current_filter = {
                "coordinates": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [
                                filter_.longitude,
                                filter_.latitude,
                            ],
                        },
                        "$maxDistance": type_distance_pair.max_distance_meters,
                    },
                },
                "types": type_distance_pair.location_type,
            }

            locations.extend(
                [
                    location
                    async for location in await self._find_with_cursor(
                        cur=cursor,
                        filter_=current_filter,
                    )
                ],
            )

        return _unique(locations)

    async def find_within_area_by_type(  # noqa: WPS211
        self,
        cursor: str,
        longitude: float,
        latitude: float,
        max_distance_meters: int,
        types: int,
    ) -> resultset.ResultSet[models_pb2.Location]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={
                "types": [types],
                "coordinates": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": max_distance_meters,
                    },
                },
            },
        )


class _PlaceNormalizer(normalizers.Normalizer):
    def denormalize(
        self,
        maybe_dict: normalizers.AnyValue,
    ) -> normalizers.AnyValue:
        maybe_dict["location"]["id"] = maybe_dict.pop("id")

        return maybe_dict

    def supports(self, fqn: str) -> bool:
        return fqn == models_pb2.Place().DESCRIPTOR.full_name

    def normalize(
        self,
        maybe_dict: Any,
    ) -> Any:
        maybe_dict["id"] = maybe_dict["location"].pop("id")

        return maybe_dict


class PlaceRepository(  # noqa: WPS215
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
    mixins.UpsertMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _proto = models_pb2.Place
    _indexes = (IndexModel([("location.coordinates", GEOSPHERE)], background=True),)

    def __init__(
        self,
        geocoding: geocoding_pb2_grpc.GeocodingServiceStub | None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._geocoding = geocoding

        normalizers.register(_PlaceNormalizer())

        super().__init__(*args, **kwargs)

    async def get_ids(self) -> frozenset[str]:
        ids = await self._execute(self._collection.distinct, "_id")
        return frozenset(str(_id) for _id in ids)

    async def get_by_ids(
        self,
        ids: Iterable[str],
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._find_with_cursor("", {"_id": {"$in": tuple(ids)}})

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def create(
        self,
        resource: models_pb2.Place,
    ) -> bool:
        if not self._geocoding:
            raise RuntimeError("Can't create without geocoding service.")

        if not resource.location.country_code:
            country_code, time_zone = await asyncio.gather(
                self._geocoding.CountryCodeLookup(
                    geocoding_pb2.CountryCodeLookupRequest(
                        coordinates=resource.location.coordinates,
                    ),
                ),
                self._geocoding.TimeZoneLookup(
                    geocoding_pb2.TimeZoneLookupRequest(
                        coordinates=resource.location.coordinates,
                    ),
                ),
            )

        if not resource.location.id:
            resource.location.id = string.uuid()

        resource.location.country_code = country_code.country_code
        resource.location.time_zone = time_zone.time_zone.id

        return await self.upsert(resource)

    async def update(self, resource: models_pb2.Place) -> bool:
        replacement = self._coder.encode(resource)
        replacement.pop("_id")

        update: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={_mongo_id_key: resource.location.id},
            replacement=replacement,
        )

        return update.acknowledged

    async def delete(self, identifier: str) -> None:
        await self._execute(
            self._collection.delete_one,
            filter={_mongo_id_key: identifier},
        )


async def create(
    repo: PlaceRepository,
    place: models_pb2.Place,
    sem: asyncio.Semaphore,
    count: int,
) -> bool:
    """Create, then release the semaphore."""
    async with sem:
        if count % 1000 == 0:
            logging.info("Places created: %s", count)

        return await repo.create(place)
