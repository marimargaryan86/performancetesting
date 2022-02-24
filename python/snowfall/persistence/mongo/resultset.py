from collections.abc import AsyncIterator
from typing import Any, Generic, Optional, TypeVar

import pymongo
from motor import motor_asyncio

from snowfall.persistence import cursor
from snowfall.persistence.mongo import coders

_mongo_id_key = "_id"
_Record = TypeVar("_Record")


class ResultSet(Generic[_Record], AsyncIterator[_Record]):
    def __init__(
        self,
        cur: motor_asyncio.AsyncIOMotorCursor,
        coder: coders.BaseCoder[_Record],
        filter_: dict[str, Any],
    ):
        self._coder = coder
        self._cursor = cur
        self._custom_sort = False
        self._filter = filter_
        self._last: Optional[str] = None

        self._cursor.sort(_mongo_id_key, pymongo.ASCENDING)

    def __aiter__(self) -> AsyncIterator[_Record]:
        return self

    async def __anext__(self) -> _Record:
        document = await self._cursor.next()
        self._last = document[_mongo_id_key]

        return self._coder.decode(document)

    async def cursor(self) -> str:
        if self._custom_sort:
            raise RuntimeError("Cursors do not yet support sorted result sets.")

        if not self._last:
            return ""

        return cursor.marshal(cursor.new(self._last, self._filter))

    def limit(self, limit: int) -> None:
        self._cursor.limit(limit)

    def sort(self, *sort: tuple[str, int]) -> None:
        self._cursor.sort(list(sort))
        self._custom_sort = True
