import abc
from copy import deepcopy
from typing import Any, Callable, Coroutine, Generic, TypeVar

import pymongo
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message
from motor import core, motor_asyncio

_proto_id_key = "id"
_mongo_id_key = "_id"


class NotFoundError(RuntimeError):
    """Raised when a resource is not found."""


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

    @property
    def _indexes(self) -> list[pymongo.IndexModel]:
        return []

    async def _create_indexes(self) -> None:
        self._has_created_indexes = True

        if not self._indexes:
            return

        await self._execute(
            self._collection.create_indexes,
            self._indexes,
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

    async def _execute_cursor(
        self,
        query: Callable[[Any], motor_asyncio.AsyncIOMotorCursor],
        *args: Any,
        **kwargs: Any,
    ) -> motor_asyncio.AsyncIOMotorCursor:
        # todo: can't run this in __init__, but this isn't pretty...
        if not self._has_created_indexes:
            await self._create_indexes()

        cursor = query(*args, **kwargs)

        cursor.limit(100)  # todo: implement proper pagination

        async for row in cursor:
            yield row


Proto = TypeVar("Proto", bound=Message)


class ProtoRepository(Generic[Proto], Repository, abc.ABC):
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

        return self._unmarshal(msg)

    @abc.abstractmethod
    def _new_model(self) -> Proto:
        raise NotImplementedError()

    def _marshal(self, msg: Proto) -> dict[str, Any]:
        fields = msg.DESCRIPTOR.fields_by_name.keys()

        # Only set created if it hasn't been set already.
        if "created" in fields and msg.created.seconds == 0:  # type: ignore[attr-defined]
            msg.created.GetCurrentTime()  # type: ignore[attr-defined]

        if "updated" in fields:
            msg.updated.GetCurrentTime()  # type: ignore[attr-defined]

        as_dict = MessageToDict(msg)

        # MongoDB expects ID to be found in "_id".
        if _proto_id_key in fields and _mongo_id_key in as_dict:
            as_dict[_mongo_id_key] = as_dict.pop(_proto_id_key)

        return as_dict

    def _unmarshal(self, as_dict: dict[str, Any]) -> Proto:
        msg = self._new_model()
        fields = msg.DESCRIPTOR.fields_by_name.keys()
        as_dict = deepcopy(as_dict)

        # MongoDB stores ID in "_id".
        if _proto_id_key in fields and _mongo_id_key in as_dict:
            as_dict[_proto_id_key] = as_dict.pop(_mongo_id_key)

        return ParseDict(as_dict, msg, ignore_unknown_fields=True)
