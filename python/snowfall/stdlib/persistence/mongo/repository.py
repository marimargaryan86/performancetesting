import abc
import datetime
import functools
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Mapping,
    Protocol,
    TypeVar,
    overload,
)

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

_DEFAULT_TIMEOUT = datetime.timedelta(seconds=10)
_MILLISECONDS_MULTIPLIER = 1000
_MAX_TIME_MS_CAMEL = "maxTimeMS"
_MAX_TIME_MS_SNAKE = "max_time_ms"
_AGGREGATE_CURSOR_CLASS = (
    motor_asyncio.AsyncIOMotorCommandCursor,
    motor_asyncio.AsyncIOMotorLatentCommandCursor,
)


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


class RepositoryProtocol(Protocol[Record]):
    @property
    def _coder(self) -> coders.BaseCoder[Record]:
        """Use to convert protobufs to BSON and back."""

    @property
    def _collection(self) -> core.AgnosticCollection:
        """Use to perform Mongo queries again."""

    async def _execute(
        self,
        query: Callable[[Any], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Use for queries to add metrics and tracing."""

    async def _find_with_cursor(
        self,
        cur: str,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[Record]:
        """Use for find queries with a filter."""


class _AbstractRepository(abc.ABC, Generic[Record]):
    _indexes: list[pymongo.IndexModel] = []
    _timeout_kwargs = {
        core.AgnosticCollection.aggregate: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.count_documents: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.create_index: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.create_indexes: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.distinct: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.drop_index: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.drop_indexes: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.estimated_document_count: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.find: _MAX_TIME_MS_SNAKE,
        core.AgnosticCollection.find_one: _MAX_TIME_MS_SNAKE,
        core.AgnosticCollection.find_one_and_delete: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.find_one_and_replace: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.find_one_and_update: _MAX_TIME_MS_CAMEL,
        core.AgnosticCollection.find_raw_batches: _MAX_TIME_MS_SNAKE,
    }

    def __init__(
        self,
        collection: motor_asyncio.AsyncIOMotorCollection,
        timeout: datetime.timedelta = _DEFAULT_TIMEOUT,
    ) -> None:
        self._collection = _configure_collection(collection)
        self._has_created_indexes = False
        self._timeout = timeout.total_seconds() * _MILLISECONDS_MULTIPLIER

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
        """Return a `Record` if the query returns a dict."""

    @overload
    async def _execute(
        self,
        query: Callable[[Any], core.AgnosticBaseCursor],
        *args: Any,
        **kwargs: Any,
    ) -> resultset.ResultSet[Record]:
        """Return a `ResultSet[Record]` if the query returns a cursor."""

    async def _execute(
        self,
        query: Callable[[Any], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # TODO: can't run this in __init__, but this isn't pretty...
        if not self._has_created_indexes:
            await self._create_indexes()

        timeout_kwarg = self._timeout_kwargs.get(query)

        if timeout_kwarg and timeout_kwarg not in kwargs:
            kwargs[timeout_kwarg] = self._timeout

        # _find_with_cursor sends a special kwarg pymongo don't like
        filter_pre_cursor = kwargs.pop("filter_pre_cursor", {})
        possible_cursor = query(*args, **kwargs)

        if isinstance(possible_cursor, motor_asyncio.AsyncIOMotorCursor):
            return resultset.DocumentResultSet[Record](
                cur=possible_cursor,
                coder=self._coder,
                filter_=filter_pre_cursor,
            )

        if isinstance(possible_cursor, _AGGREGATE_CURSOR_CLASS):
            return resultset.AggregationResultSet[Record](
                cur=possible_cursor,
                coder=self._coder,
                filter_=filter_pre_cursor,
            )

        possible_document = await possible_cursor

        if isinstance(possible_document, dict):
            return self._coder.decode(possible_document)

        return possible_document

    async def _find_nested(
        self,
        path: str,
        filter_: Mapping[str, Any] | None = None,
        cur: str | None = None,
        id_key: str = "_id",
    ) -> resultset.ResultSet[Record]:
        aggregate = []
        filter_pre_cursor = dict(filter_ or {})
        cursor_filter = filter_pre_cursor.copy()

        if cur:
            cursor_filter = self._with_cursor_filters(cur, cursor_filter)

        if cursor_filter:
            aggregate.append(
                {
                    "$match": cursor_filter,
                },
            )

        path_parts = []

        for path_part in path.split("."):
            path_parts.append(path_part)
            aggregate.append(
                {
                    "$unwind": {
                        "path": ".".join(path_parts),
                    },
                },
            )

        if cursor_filter:
            aggregate.append(
                {
                    "$match": cursor_filter,
                },
            )

        aggregate.extend(
            (
                {
                    "$replaceRoot": {
                        "newRoot": path,
                    },
                },
                {
                    "$group": {
                        "_id": "${0}".format(id_key),
                        "document": {
                            "$first": "$$ROOT",
                        },
                    },
                },
                {
                    "$replaceRoot": {
                        "newRoot": "$document",
                    },
                },
            ),
        )

        return await self._execute(
            query=self._collection.aggregate,
            pipeline=aggregate,
            filter_pre_cursor=filter_pre_cursor,
        )

    async def _find_with_cursor(
        self,
        cur: str,
        filter_: Mapping[str, Any] | None = None,
    ) -> resultset.ResultSet[Record]:
        filter_pre_cursor = dict(filter_ or {})
        cursor_filter = filter_pre_cursor.copy()

        if cur:
            cursor_filter = self._with_cursor_filters(cur, cursor_filter)

        return await self._execute(
            query=self._collection.find,
            filter=cursor_filter,
            filter_pre_cursor=filter_pre_cursor,
        )

    def _with_cursor_filters(
        self,
        cur: str,
        filter_: Mapping[str, Any],
    ) -> dict[str, Any]:
        cursor_filter = dict(filter_).copy()
        cursor_obj = cursor.unmarshal(cur, filter_)

        if cursor_obj.id == "":
            return cursor_filter

        if mongo_id_key not in filter_:
            cursor_filter[mongo_id_key] = {}

        cursor_filter[mongo_id_key]["$gt"] = cursor_obj.id

        return cursor_filter


class DefaultRepository(_AbstractRepository[Mapping[str, Any]]):
    @functools.cached_property
    def _coder(self) -> coders.NoopCoder:
        return coders.NoopCoder()


class ProtoRepository(_AbstractRepository[Proto]):
    @functools.cached_property
    def _coder(self) -> coders.ProtoCoder[Proto]:
        return coders.ProtoCoder[Proto](self._proto)

    @property
    @abc.abstractmethod
    def _proto(self) -> type[Proto]:
        raise NotImplementedError()


class PydanticRepository(_AbstractRepository[Model]):
    @functools.cached_property
    def _coder(self) -> coders.PydanticCoder[Model]:
        return coders.PydanticCoder[Model](self._model)

    @property
    @abc.abstractmethod
    def _model(self) -> type[Model]:
        raise NotImplementedError()
