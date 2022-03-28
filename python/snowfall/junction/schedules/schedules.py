import datetime
from typing import Optional

from pymongo import IndexModel, results

from snowfall.common.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import repository, resultset


class ScheduleRepository(repository.ProtoRepository[models_pb2.Schedule]):
    _proto = models_pb2.Schedule
    _indexes: list[IndexModel] = [
        IndexModel("updated_at", background=True),
        IndexModel("stops.id", background=True),
    ]

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

    async def get_last_updated_at(self) -> datetime.datetime:
        schedule: models_pb2.Schedule = await self._execute(
            self._collection.find_one,
            filter={},
            projection={
                repository.mongo_id_key: 1,
                "updated_at": 1,
            },
            sort=(("updated_at", -1),),
        )

        if not schedule:
            return datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)

        return protobuf.protobuf_to_datetime(schedule.updated_at)

    async def upsert(self, resource: models_pb2.Schedule) -> bool:
        update_result: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=self._coder.encode(resource),
            upsert=True,
        )

        return update_result.acknowledged

    async def find_schedule_by_stop_id(
        self,
        stop_id: str,
    ) -> Optional[models_pb2.Schedule]:
        schedule = await self._execute(
            self._collection.find_one,
            {"stops.id": stop_id},
        )

        if not schedule:
            return None

        return schedule

    async def find_stop_by_id(self, stop_id: str) -> Optional[models_pb2.Stop]:
        schedule = await self.find_schedule_by_stop_id(stop_id)

        if schedule is None:
            return None

        return next(
            (stop for stop in schedule.stops if stop.id == stop_id),
            None,
        )

    async def find_stop_by_previous_stop_id(
        self,
        stop_id: str,
    ) -> Optional[models_pb2.Stop]:
        schedule = await self.find_schedule_by_stop_id(stop_id)

        if schedule is None:
            return None

        for index, stop in enumerate(schedule.stops):
            if stop.id == stop_id and index < len(schedule.stops) - 1:
                return schedule.stops[index + 1]

        return None
