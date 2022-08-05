import asyncio
import copy
import functools
import uuid
from typing import Any, Mapping, Sequence

from pymongo import GEOSPHERE, IndexModel, results

from snowfall.project.junction.service.places.v1alpha import models_pb2
from snowfall.service.geodata.v1 import geocoding_pb2, geocoding_pb2_grpc
from snowfall.stdlib.persistence.mongo import coders, mixins, repository, resultset

_mongo_id_key = "_id"
_proto_id_key = "id"
_location_key = "location"

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


class LocationRepository(
    mixins.FindByIdMixin[models_pb2.Location],
    repository.ProtoRepository[models_pb2.Location],
):
    _indexes = [
        IndexModel([("coordinates", GEOSPHERE)], background=True),
    ]
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

    async def upsert(self, resource: models_pb2.Location) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged


class PlaceCoder(coders.ProtoCoder[models_pb2.Place]):
    def __init__(self) -> None:
        super().__init__(models_pb2.Place)

    def decode(self, as_dict: Mapping[str, Any]) -> models_pb2.Place:
        new_dict = dict(copy.deepcopy(as_dict))
        new_dict[_location_key][_proto_id_key] = new_dict.pop(_mongo_id_key)

        return super().decode(new_dict)

    def encode(self, proto: models_pb2.Place) -> dict[str, Any]:
        as_dict = super().encode(proto)

        if _proto_id_key in as_dict[_location_key]:
            as_dict[_mongo_id_key] = as_dict[_location_key].pop(_proto_id_key)

        return as_dict


class PlaceRepository(
    mixins.FindByIdMixin[models_pb2.Place],
    mixins.InsertMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _proto = models_pb2.Place

    def __init__(
        self,
        geocoding: geocoding_pb2_grpc.GeocodingServiceStub,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._geocoding = geocoding

        super().__init__(*args, **kwargs)

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
    ) -> models_pb2.Place:
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

        resource.location.id = str(uuid.uuid4())
        resource.location.country_code = country_code.country_code
        resource.location.time_zone = time_zone.time_zone.id

        return await self.insert(resource)

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

    @functools.cached_property
    def _coder(self) -> coders.ProtoCoder[models_pb2.Place]:
        return PlaceCoder()
