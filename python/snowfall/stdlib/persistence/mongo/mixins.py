from typing import Generic, Optional, TypeVar

from snowfall.stdlib.persistence.mongo import repository, resultset

Record = TypeVar("Record")


class AllMixin(Generic[Record]):
    async def all_(
        self: repository.RepositoryProtocol[Record],
    ) -> resultset.ResultSet[Record]:
        return await self._execute(self._collection.find)


class EstimatedCountMixin(Generic[Record]):
    async def estimated_count(self: repository.RepositoryProtocol[Record]) -> int:
        return await self._execute(self._collection.estimated_document_count)


class ExistsMixin(Generic[Record]):
    async def exists(
        self: repository.RepositoryProtocol[Record],
        identifier: str,
    ) -> bool:
        return (
            await self._execute(
                self._collection.find_one,
                {repository.mongo_id_key: identifier},
                {repository.mongo_id_key: 1},
            )
            is not None
        )


class FindByIdMixin(Generic[Record]):
    async def find_by_id(
        self: repository.RepositoryProtocol[Record],
        document_id: str,
    ) -> Optional[Record]:
        return await self._execute(
            self._collection.find_one,
            {
                "_id": document_id,
            },
        )


class InsertMixin(Generic[Record]):
    async def insert(
        self: repository.RepositoryProtocol[Record],
        document: Record,
    ) -> Record:
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(document),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return document
