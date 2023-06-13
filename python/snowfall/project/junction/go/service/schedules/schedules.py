from collections.abc import Sequence

from pymongo import IndexModel

from snowfall.project.junction.go.v1alpha import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset

LEGS_ID = "legs._id"


class LegRepository(repository.ProtoRepository[models_pb2.Leg]):
    _proto = models_pb2.Leg
    _nested_path = "legs"
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

        return await self._find_with_cursor(
            filter_=filter_,
            cur=cursor,
        )

    async def find_by_id(self, document_id: str) -> models_pb2.Leg | None:
        legs = await self._find_with_cursor(
            filter_={
                LEGS_ID: {
                    "$eq": document_id,
                },
            },
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
