import copy
import functools
import uuid
from typing import Any, Mapping

from pymongo import GEOSPHERE, IndexModel, results

from snowfall.stdlib.persistence.mongo import coders, mixins, repository, resultset
from snowfall.stdlib.v1alpha import models_pb2

_mongo_id_key = "_id"
_proto_id_key = "id"
_place_key = "place"

_NAMESPACE = uuid.UUID("5190984e-4ab7-411e-96f6-2848cc5d63e1")


class PlaceRepository(
    mixins.FindByIdMixin[models_pb2.Place],
    repository.ProtoRepository[models_pb2.Place],
):
    _indexes = [
        IndexModel([("coordinates", GEOSPHERE)], background=True),
    ]
    _proto = models_pb2.Place

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Place]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def upsert(self, resource: models_pb2.Place) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged


class CuratedPlaceCoder(coders.ProtoCoder[models_pb2.CuratedPlace]):
    def __init__(self) -> None:
        super().__init__(models_pb2.CuratedPlace)

    def decode(self, as_dict: Mapping[str, Any]) -> models_pb2.CuratedPlace:
        new_dict = dict(copy.deepcopy(as_dict))
        new_dict[_place_key][_proto_id_key] = new_dict.pop(_mongo_id_key)

        return super().decode(new_dict)

    def encode(self, proto: models_pb2.CuratedPlace) -> dict[str, Any]:
        as_dict = super().encode(proto)

        if _proto_id_key in as_dict[_place_key]:
            as_dict[_mongo_id_key] = as_dict[_place_key].pop(_proto_id_key)

        return as_dict


class CuratedPlaceRepository(
    mixins.FindByIdMixin[models_pb2.CuratedPlace],
    mixins.InsertMixin[models_pb2.CuratedPlace],
    repository.ProtoRepository[models_pb2.CuratedPlace],
):
    _proto = models_pb2.CuratedPlace

    async def find(
        self,
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.CuratedPlace]:
        return await self._find_with_cursor(
            cur=cursor,
        )

    async def create(
        self,
        resource: models_pb2.CuratedPlace,
    ) -> models_pb2.CuratedPlace:
        resource.place.id = str(uuid.uuid5(_NAMESPACE, resource.place.name))

        return await self.insert(resource)

    async def update(self, place_id: str, resource: models_pb2.CuratedPlace) -> bool:
        update: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={_mongo_id_key: place_id},
            replacement=self._coder.encode(resource),
        )

        return update.acknowledged

    async def delete(self, place_id: str) -> None:
        await self._execute(
            self._collection.delete_one,
            filter={_mongo_id_key: place_id},
        )

    @functools.cached_property
    def _coder(self) -> coders.ProtoCoder[models_pb2.CuratedPlace]:
        return CuratedPlaceCoder()
