import abc
from collections.abc import AsyncIterator, Mapping
from typing import Any, Generic, TypeVar, cast

import pymongo
from motor import core, motor_asyncio

from snowfall.stdlib.persistence import cursor
from snowfall.stdlib.persistence.mongo import coders

_mongo_id_key = "_id"
_proto_id_key = "id"
_Record = TypeVar("_Record")


class ResultSet(abc.ABC, Generic[_Record], AsyncIterator[_Record]):
    def __init__(
        self,
        cur: core.AgnosticBaseCursor,
        coder: coders.BaseCoder[_Record],
        filter_: Mapping[str, Any],
        sort: tuple[str, int] | None = None,
    ):
        self._coder = coder
        self._cursor = cur
        self._manual_sort = False
        self._fetched = 0
        self._filter = filter_
        self._sort = sort
        self._custom_sort_field = None
        self._last_sort_value = None
        self._last: str | None = None
        self._limit = 0

        if sort and sort[0] != _mongo_id_key:
            self._custom_sort_field = sort[0]

    def __aiter__(self) -> AsyncIterator[_Record]:
        return self

    async def __anext__(self) -> _Record:
        document = cast(dict[str, Any], await self._cursor.__anext__())  # noqa: WPS609
        self._last = document.get(_mongo_id_key, document.get(_proto_id_key))

        if self._custom_sort_field:
            self._last_sort_value = document.get(self._custom_sort_field)

        self._fetched += 1

        return self._coder.decode(document)

    async def cursor(self) -> str:
        if self._manual_sort:
            raise RuntimeError("Cursors do not support manually sorted result sets.")

        return cursor.marshal(
            cursor.new(
                identifier=self._last or "",
                filter_=self._filter,
                sort=self._sort,
                sort_value=self._last_sort_value,
            ),
        )

    async def take(self) -> _Record:
        return await self.__anext__()

    @abc.abstractmethod
    def limit(self, limit: int) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def sort(self, *sort: tuple[str, int]) -> None:
        raise NotImplementedError()


class DocumentResultSet(ResultSet[_Record]):
    def __init__(
        self,
        cur: motor_asyncio.AsyncIOMotorCursor,
        coder: coders.BaseCoder[_Record],
        filter_: Mapping[str, Any],
        sort: tuple[str, int] | None,
    ) -> None:
        super().__init__(cur, coder, filter_, sort)

        self._cur = cur
        sort_fields = []

        if sort:
            sort_fields.append(sort)

        if not sort_fields or sort_fields[0][0] != _mongo_id_key:
            sort_fields = [*sort_fields, (_mongo_id_key, pymongo.ASCENDING)]

        self._cur.sort(sort_fields)

    def limit(self, limit: int) -> None:
        self._limit = limit

        self._cur.limit(limit)

    def sort(self, *sort: tuple[str, int]) -> None:
        self._cur.sort(list(sort))
        self._manual_sort = True


class AggregationResultSet(ResultSet[_Record]):
    async def __anext__(self) -> _Record:
        if self._limit and self._fetched >= self._limit:
            raise StopAsyncIteration()

        return await super().__anext__()

    def limit(self, limit: int) -> None:
        self._limit = limit

    def sort(self, *sort: tuple[str, int]) -> None:
        raise RuntimeError("Sorted result sets are not supported on aggregations.")
