from pymongo import results

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo.repository import ProtoRepository


class ScheduleRepository(ProtoRepository[models_pb2.Schedule]):
    _proto = models_pb2.Schedule

    async def upsert(self, resource: models_pb2.Schedule) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged
