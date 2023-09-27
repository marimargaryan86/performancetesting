from collections.abc import Sequence

from pymongo import results

from snowfall.project.junction.go.service.resellers.v1 import models_pb2
from snowfall.stdlib.persistence.mongo import mixins, repository, resultset


class ResellerRepository(
    mixins.FindByIdMixin[models_pb2.Reseller],
    mixins.InsertMixin[models_pb2.Reseller],
    repository.ProtoRepository[models_pb2.Reseller],
):
    _proto = models_pb2.Reseller

    async def find(
        self,
        cursor: str,
        identifiers: Sequence[str] | None = None,
    ) -> resultset.ResultSet[models_pb2.Reseller]:
        return await self._find_with_cursor(
            cur=cursor,
            filter_={"_id": {"$in": identifiers}} if identifiers else None,
        )

    async def update(
        self,
        resource: models_pb2.Reseller,
    ) -> bool:
        replacement = self._coder.encode(resource)
        replacement.pop("_id")

        update: results.UpdateResult = await self._execute(
            self._collection.replace_one,
            filter={"_id": resource.id},
            replacement=replacement,
        )

        return update.acknowledged

    async def delete(self, identifier: str) -> None:
        await self._execute(
            self._collection.delete_one,
            filter={"_id": identifier},
        )
