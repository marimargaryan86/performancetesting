from __future__ import annotations

from typing import Generic, TypeVar

from snowfall.stdlib.persistence.mongo import repository

Record = TypeVar("Record")


class FindByIdMixin(Generic[Record]):
    async def find_by_id(
        self: repository.RepositoryProtocol[Record],
        document_id: str,
        reseller_id: str = "",
    ) -> Record | None:
        query = {
            "_id": document_id,
        }
        if reseller_id:
            query["reseller_id"] = reseller_id

        return await self._execute(
            self._collection.find_one,
            query,
        )
