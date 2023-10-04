from __future__ import annotations

import datetime
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

import pymongo

from snowfall.stdlib.persistence.mongo import repository, resultset
from snowfall.stdlib.v1 import amqp_pb2

Record = TypeVar("Record")


class AllMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def all_(
        self,
        cursor: str | None = None,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[Record]:
        return await self._find_with_cursor(cur=cursor or "", sort=sort)


class EstimatedCountMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def estimated_count(self) -> int:
        return await self._execute(self._collection.estimated_document_count)


class ExistsMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def exists(
        self,
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


class FindByIdMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def find_by_id(
        self,
        document_id: str,
        selector: str = "_id",
    ) -> Record | None:
        return await self._execute(
            self._collection.find_one,
            {
                selector: document_id,
            },
        )


class InsertMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def insert(
        self,
        document: Record,
    ) -> Record:
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(document),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return document


class InsertManyMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def insert_many(
        self,
        documents: Sequence[Record],
        **kwargs: Any,
    ) -> Sequence[Record]:
        inserts = await self._execute(
            self._collection.insert_many,
            [self._coder.encode(document) for document in documents],
            **kwargs,
        )

        if not inserts.acknowledged:
            raise RuntimeError()

        return documents


class StatusMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def mark_as_completed(
        self,
        document_id: str,
    ) -> Record:
        return await self._execute(
            self._collection.find_one_and_update,
            {"_id": document_id},
            {
                "$set": {
                    "status": amqp_pb2.Trackable.STATUS_COMPLETED,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )

    async def mark_as_failed(
        self,
        document_id: str,
    ) -> Record:
        return await self._execute(
            self._collection.find_one_and_update,
            {"_id": document_id},
            {
                "$set": {
                    "status": amqp_pb2.Trackable.STATUS_FAILED,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )

    async def mark_as_processing(
        self,
        document_id: str,
    ) -> Record:
        return await self._execute(
            self._collection.find_one_and_update,
            {"_id": document_id},
            {
                "$set": {
                    "status": amqp_pb2.Trackable.STATUS_PROCESSING,
                    "updated_at": datetime.datetime.now(tz=datetime.UTC),
                },
            },
            return_document=pymongo.ReturnDocument.AFTER,
        )


class UpsertMixin(Generic[Record], repository.RepositoryProtocol[Record]):
    async def upsert(
        self,
        document: Record,
    ) -> bool:
        encoded = self._coder.encode(document)
        upsert = await self._execute(
            self._collection.replace_one,
            filter={"_id": encoded["_id"]},
            replacement=encoded,
            upsert=True,
        )

        return upsert.acknowledged
