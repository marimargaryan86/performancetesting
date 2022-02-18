from pymongo import GEOSPHERE, IndexModel, results

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo import repository


class PlaceRepository(repository.ProtoRepository[models_pb2.Place]):
    _indexes = [
        IndexModel([("coordinates", GEOSPHERE)], background=True),
    ]
    _proto = models_pb2.Place

    async def upsert(self, resource: models_pb2.Place) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged
