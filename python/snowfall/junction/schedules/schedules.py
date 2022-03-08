from pymongo import results

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence.mongo import repository, resultset


class ScheduleRepository(repository.ProtoRepository[models_pb2.Schedule]):
    _proto = models_pb2.Schedule

    async def find(
        self,
        ids: list[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Schedule]:
        filter_ = (
            {
                repository.mongo_id_key: {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_with_cursor(
            cur=cursor,
            filter_=filter_,
        )

    async def upsert(self, resource: models_pb2.Schedule) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged
