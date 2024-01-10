import abc
import asyncio
import copy
import datetime
import functools
import types
from collections.abc import Callable, Mapping
from typing import Any, Generic, Protocol, TypeVar, cast

import pydantic
import pymongo
from bson import json_util
from google.protobuf.message import Message
from motor import core, motor_asyncio

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.persistence.mongo import coders, resultset
from snowfall.stdlib.v1 import cursor_pb2

_proto_id_key = "id"
mongo_id_key = "_id"

Model = TypeVar("Model", bound=pydantic.BaseModel)
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
_DIRECTIONS = types.MappingProxyType(
    {
        pymongo.ASCENDING: "$gt",
        pymongo.DESCENDING: "$lt",
    },
)


class UnindexedSortFieldError(Exception):
    """Raised when a sort field is not indexed."""


def with_cursor_filters(
    cursor_obj: cursor_pb2.Cursor,
    filter_: Mapping[str, Any],
    sort: tuple[str, int] | None = None,
    path: str | None = None,
) -> dict[str, Any]:
    cursor_filter = dict(copy.deepcopy(filter_))

    if cursor_obj.id == "":
        return cursor_filter

    if not sort:
        sort = (mongo_id_key, pymongo.ASCENDING)

    if path:
        sort = ("{0}.{1}".format(path, sort[0]), sort[1])
        prefixed_id = "{0}.{1}".format(path, mongo_id_key)
    else:
        prefixed_id = mongo_id_key

    if sort[0] != prefixed_id:
        or_block: list[Any] = []
        if "$or" not in cursor_filter:
            cursor_filter["$or"] = or_block
        else:
            cursor_filter["$and"] = [
                {
                    "$or": cursor_filter.pop("$or"),
                },
                {
                    "$or": or_block,
                },
            ]
        sort_value = json_util.loads(cursor_obj.sort_value)

        or_block.extend(
            (
                {sort[0]: {_DIRECTIONS[sort[1]]: sort_value}},
                {
                    sort[0]: sort_value,
                    prefixed_id: {_DIRECTIONS[pymongo.ASCENDING]: cursor_obj.id},
                },
            ),
        )

        return cursor_filter

    if prefixed_id not in cursor_filter:
        cursor_filter[prefixed_id] = {}

    cursor_filter[prefixed_id][_DIRECTIONS[sort[1]]] = cursor_obj.id

    return cursor_filter


def create_sort(
    sort: tuple[str, int] | None = None,
) -> list[tuple[str, int]]:
    sort_fields = []

    if sort:
        sort_fields.append(sort)

    if not sort_fields or sort_fields[0][0] != mongo_id_key:
        sort_fields = [
            *sort_fields,
            (mongo_id_key, pymongo.ASCENDING),
        ]

    return sort_fields


def _configure_collection(
    collection: core.AgnosticCollection,
) -> core.AgnosticCollection:
    try:
        return cast(
            core.AgnosticCollection,
            collection.with_options(
                codec_options=collection.codec_options.with_options(
                    tz_aware=True,
                    tzinfo=datetime.UTC,
                ),
            ),
        )
    except NotImplementedError:
        # Mongomock does not handle custom tzinfo yet.
        return collection


class RepositoryProtocol(Protocol[Record]):
    _collection: core.AgnosticCollection

    @property
    def _coder(self) -> coders.BaseCoder[Record]:
        """Use to convert protobufs to BSON and back."""

    async def _execute(
        self,
        query: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Use for queries to add metrics and tracing."""

    async def _find_with_cursor(
        self,
        cur: str,
        filter_: Mapping[str, Any] | None = None,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[Record]:
        """Use for find queries with a filter."""


class _AbstractRepository(abc.ABC, Generic[Record]):
    _nested_path: str | None = None
    _indexes: tuple[pymongo.IndexModel, ...] = ()
    _timeout_kwargs = types.MappingProxyType(
        {
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
        },
    )

    def __init__(
        self,
        collection: core.AgnosticCollection,
        timeout: datetime.timedelta = _DEFAULT_TIMEOUT,
    ) -> None:
        self._collection = _configure_collection(collection)
        self._timeout = timeout.total_seconds() * _MILLISECONDS_MULTIPLIER
        self._valid_sort_fields = [
            index_key for index in self._indexes for index_key in index.document["key"]
        ]
        self._valid_sort_fields.append(mongo_id_key)
        self._root_path = "${0}".format((self._nested_path or "").removeprefix("$"))
        self._nested_path_parts = self._root_path.split(".")
        self._clean_path = self._root_path.removeprefix("$")
        self.indexes_created_event = asyncio.Event()
        # TODO(sam.b): Probably use aiojobs in future to manage this task properly.
        asyncio.create_task(  # type: ignore[unused-awaitable]  # noqa: RUF006
            self._create_indexes(),
        )

    async def _create_indexes(self) -> None:
        if not self._indexes:
            self.indexes_created_event.set()
            return

        await self._execute(
            self._collection.create_indexes,
            list(self._indexes),
            skip_indexes=True,
        )
        self.indexes_created_event.set()

    @property
    @abc.abstractmethod
    def _coder(self) -> coders.BaseCoder[Record]:
        raise NotImplementedError()

    async def _execute(
        self,
        query: Callable[..., Any],
        *args: Any,
        unmarshalled_cursor: cursor_pb2.Cursor | None = None,
        skip_indexes: bool = False,
        **kwargs: Any,
    ) -> Any:
        if not skip_indexes:
            await self.indexes_created_event.wait()

        timeout_kwarg = self._timeout_kwargs.get(query)

        if timeout_kwarg and timeout_kwarg not in kwargs:
            kwargs[timeout_kwarg] = self._timeout

        # _find_with_cursor sends a special kwarg pymongo don't like
        filter_pre_cursor = kwargs.pop("filter_pre_cursor", {})
        sort = kwargs.pop("sort", None)

        if sort:
            index_field = sort[0]

            if self._clean_path:
                index_field = "{0}.{1}".format(self._clean_path, sort[0])

            if index_field not in self._valid_sort_fields:
                raise UnindexedSortFieldError(
                    "Field {0} is unindexed.".format(index_field),
                )

        return await self._parse_result(
            possible_cursor=query(*args, **kwargs),
            filter_=filter_pre_cursor,
            sort=sort,
            unmarshalled_cursor=unmarshalled_cursor,
        )

    async def _parse_result(
        self,
        possible_cursor: Any,
        filter_: Mapping[str, Any],
        sort: tuple[str, int] | None,
        unmarshalled_cursor: cursor_pb2.Cursor | None = None,
    ) -> Any:
        if isinstance(possible_cursor, motor_asyncio.AsyncIOMotorCursor):
            return resultset.DocumentResultSet[Record](
                cur=possible_cursor,
                coder=self._coder,
                filter_=filter_,
                sort=sort,
                previous_cursor=unmarshalled_cursor,
            )

        if isinstance(possible_cursor, _AGGREGATE_CURSOR_CLASS):
            return resultset.AggregationResultSet[Record](
                cur=possible_cursor,
                coder=self._coder,
                filter_=filter_,
                sort=sort,
                previous_cursor=unmarshalled_cursor,
            )

        possible_document = await possible_cursor

        if isinstance(possible_document, dict):
            return self._coder.decode(possible_document)

        return possible_document

    async def _find_with_cursor(
        self,
        cur: str | None = None,
        filter_: Mapping[str, Any] | None = None,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[Record]:
        if self._nested_path:
            return await self._find_nested(
                cur=cur,
                filter_=filter_,
                sort=sort,
            )

        filter_pre_cursor = dict(filter_ or {})
        cursor_filter = copy.deepcopy(filter_pre_cursor)
        unmarshalled_cursor = None

        if cur:
            unmarshalled_cursor = cursor.unmarshal(cur, filter_pre_cursor, sort)
            cursor_filter = with_cursor_filters(
                unmarshalled_cursor,
                cursor_filter,
                sort,
            )

        return await self._execute(
            query=self._collection.find,
            filter=cursor_filter,
            filter_pre_cursor=filter_pre_cursor,
            sort=sort,
            unmarshalled_cursor=unmarshalled_cursor,
        )

    async def _find_nested(
        self,
        filter_: Mapping[str, Any] | None = None,
        cur: str | None = None,
        sort: tuple[str, int] | None = None,
    ) -> resultset.ResultSet[Record]:
        aggregate = []
        filter_pre_cursor = dict(filter_ or {})
        cursor_filter = filter_pre_cursor.copy()
        unmarshalled_cursor = None

        if cur:
            unmarshalled_cursor = cursor.unmarshal(cur, filter_pre_cursor, sort)
            cursor_filter = with_cursor_filters(
                cursor_obj=unmarshalled_cursor,
                filter_=cursor_filter,
                sort=sort,
                path=self._clean_path,
            )

        if cursor_filter:
            aggregate.append(
                {
                    "$match": cursor_filter,
                },
            )

        path_parts = []

        for path_part in self._nested_path_parts:
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
                        "newRoot": self._root_path,
                    },
                },
                {
                    "$group": {
                        mongo_id_key: "${0}".format(mongo_id_key),
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
                {
                    "$sort": {
                        sort_field[0]: sort_field[1] for sort_field in create_sort(sort)
                    },
                },
            ),
        )

        return await self._execute(
            query=self._collection.aggregate,
            pipeline=aggregate,
            filter_pre_cursor=filter_pre_cursor,
            sort=sort,
            unmarshalled_cursor=unmarshalled_cursor,
        )


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
