import abc
import copy
import datetime
import functools
from typing import Any, Awaitable, Callable, Generic, Optional, Type, TypeVar, overload

import pymongo
from bson import codec_options
from google.protobuf.message import Message
from motor import core, motor_asyncio
from pydantic import BaseModel

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.persistence.mongo import coders, resultset

_proto_id_key = "id"
mongo_id_key = "_id"

Model = TypeVar("Model", bound=BaseModel)
Proto = TypeVar("Proto", bound=Message)
Record = TypeVar("Record")
_MongoDict = dict[str, Any]


def _configure_collection(
    collection: motor_asyncio.AsyncIOMotorCollection,
) -> core.AgnosticCollection:
    return collection.database.get_collection(
        name=collection.name,
        codec_options=codec_options.CodecOptions(
            tz_aware=True,
            tzinfo=datetime.timezone.utc,
        ),
    )


class _AbstractRepository(abc.ABC, Generic[Record]):  # noqa: WPS214
    _indexes: list[pymongo.IndexModel] = []

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
    ) -> None:
        self._has_created_indexes = False
        self._collection = _configure_collection(collection)

    async def all_(self) -> resultset.ResultSet[Record]:
        return await self._execute(self._collection.find)

    async def estimated_count(self) -> int:
        return await self._execute(self._collection.estimated_document_count)

    async def exists(self, identifier: str) -> bool:
        return (
            await self._execute(
                self._collection.find_one,
                {mongo_id_key: identifier},
                {mongo_id_key: 1},
            )
            is not None
        )

    async def find_by_id(self, document_id: str) -> Optional[Record]:
        return await self._execute(
            self._collection.find_one,
            {
                "_id": document_id,
            },
        )

    async def insert(self, document: Record) -> Record:
        insert = await self._execute(
            self._collection.insert_one,
            self._coder.encode(document),
        )

        if not insert.acknowledged:
            raise RuntimeError()

        return document

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
    ) -> resultset.ResultSet[Record]:
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

        # _find_with_cursor sends a special kwarg pymongo don't like
        filter_pre_cursor = kwargs.pop("filter_pre_cursor", {})
        possible_cursor = query(*args, **kwargs)

        if isinstance(possible_cursor, motor_asyncio.AsyncIOMotorCursor):
            return resultset.ResultSet[Record](
                cur=possible_cursor,
                coder=self._coder,
                filter_=filter_pre_cursor,
            )

        possible_document = await possible_cursor

        if isinstance(possible_document, dict):
            return self._coder.decode(possible_document)

        return possible_document

    async def _find_with_cursor(
        self,
        cur: str,
        filter_: Optional[dict[str, Any]] = None,
    ) -> resultset.ResultSet[Record]:
        if filter_ is None:
            filter_ = {}

        filter_pre_cursor = copy.deepcopy(filter_)

        if cur:
            cursor_obj = cursor.unmarshal(cur, filter_)

            if mongo_id_key not in filter_:
                filter_[mongo_id_key] = {}

            filter_[mongo_id_key]["$gt"] = cursor_obj.id

        return await self._execute(
            query=self._collection.find,
            filter=filter_,
            filter_pre_cursor=filter_pre_cursor,
        )


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
