from typing import Optional

from pymongo import results

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo import ProtoRepository, ResultSet


class PlaceRepository(ProtoRepository[models_pb2.Place]):
    async def find(
        self,
        cur: Optional[models_pb2.Cursor] = None,
    ) -> ResultSet[models_pb2.Place]:
        return await self._execute_cursor(self._collection.find, cur)

    async def upsert(self, resource: models_pb2.Place) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._marshal(resource),
            upsert=True,
        )

        return update_result.acknowledged

    def _new_model(self) -> models_pb2.Place:
        return models_pb2.Place()
