from typing import AsyncIterator

from pymongo import results

from snowfall.common.v1alpha.models_pb2 import Place
from snowfall.persistence.mongo import ProtoRepository


class PlaceRepository(ProtoRepository[Place]):
    async def find(self) -> AsyncIterator[Place]:
        async for place in self._execute_cursor(self._collection.find):
            yield self._unmarshal(place)

    async def upsert(self, resource: Place) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.update_one,
            filter={"_id": resource.id},
            update={"$set": self._marshal(resource)},
            upsert=True,
        )

        return update_result.acknowledged

    def _new_model(self) -> Place:
        return Place()
