import abc
import functools
from collections.abc import AsyncIterator
from typing import Any, Awaitable, Callable, Generic, Optional, Type, TypeVar, overload

import pymongo
from google.protobuf.message import Message
from motor import core, motor_asyncio
from pydantic import BaseModel

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence import cursor
from snowfall.persistence.mongo import coders

_proto_id_key = "id"
_mongo_id_key = "_id"

Model = TypeVar("Model", bound=BaseModel)
Proto = TypeVar("Proto", bound=Message)
Record = TypeVar("Record")
_MongoDict = dict[str, Any]


class ResultSet(Generic[Record], AsyncIterator[Record]):
    def __init__(
        self,
        cur: motor_asyncio.AsyncIOMotorCursor,
        coder: coders.BaseCoder[Record],
    ):
        self._coder = coder
        self._cursor = cur
        self._last: Optional[str] = None

        self._cursor.sort(_mongo_id_key, pymongo.ASCENDING)

    def __aiter__(self) -> AsyncIterator[Record]:
        return self

    async def __anext__(self) -> Record:
        document = await self._cursor.next()
        self._last = document[_mongo_id_key]

        return self._coder.decode(document)

    async def cursor(self) -> Optional[models_pb2.Cursor]:
        if not self._last:
            return None

        return cursor.new(self._last, "$gt")

    def limit(self, limit: int) -> None:
        self._cursor.limit(limit)

    def sort(self, *sort: tuple[str, int]) -> None:
        self._cursor.sort(list(sort))


class _AbstractRepository(abc.ABC, Generic[Record]):
    _indexes: list[pymongo.IndexModel] = []

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
    ) -> None:
        self._collection: core.AgnosticCollection = collection
        self._has_created_indexes = False

    async def exists(self, identifier: str) -> bool:
        return (
            await self._execute(
                self._collection.find_one,
                {_mongo_id_key: identifier},
                {_mongo_id_key: 1},
            )
            is not None
        )

    async def find_with_cursor(
        self,
        cur: Optional[models_pb2.Cursor] = None,
    ) -> ResultSet[Record]:
        clause = {}

        if cur:
            clause = {
                _mongo_id_key: {
                    cur.clause: cur.id,
                },
            }

        return await self._execute(self._collection.find, clause)

    async def find_by_id(self, document_id: str) -> Optional[Record]:
        return await self._execute(
            self._collection.find_one,
            {
                "_id": document_id,
            },
        )

    async def _create_indexes(self) -> None:
        self._has_created_indexes = True

        if not self._indexes:
            return

        await self._execute(
            self._collection.create_indexes,
            self._indexes,
        )

    @property
    @abc.abstractmethod
    def _coder(self) -> coders.BaseCoder[Record]:
        raise NotImplementedError()

    @overload
    async def _execute(  # type: ignore[misc]
        self,
        query: Callable[[Any], Awaitable[_MongoDict]],
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Return a ``Record`` if the query returns a dict."""

    @overload
    async def _execute(
        self,
        query: Callable[[Any], motor_asyncio.AsyncIOMotorCursor],
        *args: Any,
        **kwargs: Any,
    ) -> ResultSet[Record]:
        """Return a ``ResultSet[Record]`` if the query returns a cursor."""

    async def _execute(
        self,
        query: Callable[[Any], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # todo: can't run this in __init__, but this isn't pretty...
        if not self._has_created_indexes:
            await self._create_indexes()

        possible_cursor = query(*args, **kwargs)

        if isinstance(possible_cursor, motor_asyncio.AsyncIOMotorCursor):
            return ResultSet[Record](
                possible_cursor,
                self._coder,
            )

        possible_document = await possible_cursor

        if isinstance(possible_document, dict):
            return self._coder.decode(possible_document)

        return possible_document


class DefaultRepository(_AbstractRepository[dict[str, Any]]):
    @functools.cached_property
    def _coder(self) -> coders.NoopCoder:
        return coders.NoopCoder()


class ProtoRepository(_AbstractRepository[Proto]):
    @functools.cached_property
    def _coder(self) -> coders.ProtoCoder[Proto]:
        return coders.ProtoCoder[Proto](self._proto)

    @property
    @abc.abstractmethod
    def _proto(self) -> Type[Proto]:
        raise NotImplementedError()


class PydanticRepository(_AbstractRepository[Model]):
    @functools.cached_property
    def _coder(self) -> coders.PydanticCoder[Model]:
        return coders.PydanticCoder[Model](self._model)

    @property
    @abc.abstractmethod
    def _model(self) -> Type[Model]:
        raise NotImplementedError()
