import abc
from copy import deepcopy
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Optional,
    TypeVar,
)

import pymongo
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message
from motor import core, motor_asyncio

from snowfall.common.v1alpha import models_pb2
from snowfall.persistence import cursor
from snowfall.persistence.mongo import normalizers

_proto_id_key = "id"
_mongo_id_key = "_id"

Proto = TypeVar("Proto", bound=Message)


class NotFoundError(RuntimeError):
    """Raised when a resource is not found."""


class ResultSet(Generic[Proto]):
    def __init__(
        self,
        cur: motor_asyncio.AsyncIOMotorCursor,
        unmarshal: Callable[[dict[str, Any]], Awaitable[Proto]],
    ):
        self._cursor = cur
        self._last: Optional[str] = None
        self._unmarshal = unmarshal

        self._cursor.sort(_mongo_id_key, pymongo.ASCENDING)

    async def cursor(self) -> Optional[models_pb2.Cursor]:
        if not self._last:
            return None

        return cursor.new(self._last, "$gt")

    async def records(self, limit: int) -> AsyncIterator[Proto]:
        self._cursor.limit(limit)

        async for record in self._cursor:
            self._last = record[_mongo_id_key]

            yield await self._unmarshal(record)


class Repository(abc.ABC):
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

    async def _indexes(self) -> list[pymongo.IndexModel]:
        return []

    async def _create_indexes(self) -> None:
        self._has_created_indexes = True
        indexes = await self._indexes()

        if not indexes:
            return

        await self._execute(
            self._collection.create_indexes,
            indexes,
        )

    async def _execute(
        self,
        query: Callable[[Any], Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # todo: can't run this in __init__, but this isn't pretty...
        if not self._has_created_indexes:
            await self._create_indexes()

        return await query(*args, **kwargs)


class ProtoRepository(Generic[Proto], Repository, abc.ABC):
    _datetime_cache: dict[str, list[str]] = {}
    _normalizers = (
        normalizers.CoordinatesNormalizer(),
        normalizers.TimestampNormalizer(),
    )

    async def get_by_id(
        self,
        identifier: str,
    ) -> Proto:
        msg = await self._execute(
            self._collection.find_one,
            {"_id": identifier},
        )

        if msg is None:
            raise NotFoundError()

        return await self._unmarshal(msg)

    async def _execute_cursor(
        self,
        query: Callable[[Any], motor_asyncio.AsyncIOMotorCursor],
        cur: Optional[models_pb2.Cursor],
        *args: Any,
        **kwargs: Any,
    ) -> ResultSet[Proto]:
        # todo: can't run this in __init__, but this isn't pretty...
        if not self._has_created_indexes:
            await self._create_indexes()

        if cur:
            if not args:
                args = ({},)

            if _mongo_id_key not in args[0]:
                args[0][_mongo_id_key] = {}

            args[0][_mongo_id_key][cur.clause] = cur.id

        return ResultSet[Proto](query(*args, **kwargs), self._unmarshal)

    @abc.abstractmethod
    def _new_model(self) -> Proto:
        raise NotImplementedError()

    async def _marshal(self, msg: Proto) -> dict[str, Any]:
        fields = msg.DESCRIPTOR.fields_by_name.keys()

        # Only set created if it hasn't been set already.
        if "created_at" in fields and msg.created.seconds == 0:  # type: ignore[attr-defined]
            msg.created_at.GetCurrentTime()  # type: ignore[attr-defined]

        if "updated_at" in fields:
            msg.updated_at.GetCurrentTime()  # type: ignore[attr-defined]

        as_dict = MessageToDict(msg, preserving_proto_field_name=True)

        # MongoDB expects ID to be found in "_id".
        if _proto_id_key in fields and _proto_id_key in as_dict:
            as_dict[_mongo_id_key] = as_dict.pop(_proto_id_key)

        for normalizer in self._normalizers:
            as_dict = await normalizer.normalize(msg.DESCRIPTOR, as_dict)

        return as_dict

    async def _unmarshal(self, as_dict: dict[str, Any]) -> Proto:
        msg = self._new_model()
        fields = msg.DESCRIPTOR.fields_by_name.keys()
        as_dict = deepcopy(as_dict)

        # MongoDB stores ID in "_id".
        if _proto_id_key in fields and _mongo_id_key in as_dict:
            as_dict[_proto_id_key] = as_dict.pop(_mongo_id_key)

        for normalizer in self._normalizers:
            as_dict = await normalizer.denormalize(msg.DESCRIPTOR, as_dict)

        return ParseDict(as_dict, msg, ignore_unknown_fields=True)
