from typing import Optional

from pymongo import GEOSPHERE, IndexModel, results

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo import repository


class PlaceRepository(repository.ProtoRepository[models_pb2.Place]):
    async def find(
        self,
        cur: Optional[models_pb2.Cursor] = None,
    ) -> repository.ResultSet[models_pb2.Place]:
        return await self._execute_cursor(self._collection.find, cur)

    async def upsert(self, resource: models_pb2.Place) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=await self._marshal(resource),
            upsert=True,
        )

        return update_result.acknowledged

    async def _indexes(self) -> list[IndexModel]:
        return [
            IndexModel([("coordinates", GEOSPHERE)], background=True),
        ]

    def _new_model(self) -> models_pb2.Place:
        return models_pb2.Place()
