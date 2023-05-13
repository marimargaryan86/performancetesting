import datetime
from typing import Sequence

from pymongo import IndexModel

from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.format import protobuf
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

LEGS_ID = "legs._id"


class LegRepository(repository.ProtoRepository[models_pb2.Leg]):
    _proto = models_pb2.Leg
    _indexes: list[IndexModel] = [
        IndexModel(LEGS_ID, background=True, unique=True),
    ]

    async def find(
        self,
        ids: Sequence[str],
        cursor: str,
    ) -> resultset.ResultSet[models_pb2.Leg]:
        filter_ = (
            {
                LEGS_ID: {
                    "$in": ids,
                },
            }
            if ids
            else {}
        )

        return await self._find_nested(
            path="$legs",
            filter_=filter_,
            cur=cursor,
            id_key="_id",
        )

    async def find_by_id(self, document_id: str) -> models_pb2.Leg | None:
        legs = await self._find_nested(
            path="$legs",
            filter_={
                LEGS_ID: {
                    "$eq": document_id,
                },
            },
            id_key="_id",
        )

        try:
            return await legs.take()
        except StopAsyncIteration:
            return None


class ScheduleRepository(
    mixins.AllMixin[models_pb2.Schedule],
    mixins.FindByIdMixin[models_pb2.Schedule],
    repository.ProtoRepository[models_pb2.Schedule],
):
    _proto = models_pb2.Schedule
    _indexes: list[IndexModel] = [
        IndexModel("updated_at", background=True),
    ]

    async def find(
        self,
        ids: Sequence[str],
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
        schedule: models_pb2.Schedule | None = await self._execute(
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
