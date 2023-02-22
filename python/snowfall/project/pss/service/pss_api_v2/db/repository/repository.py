from typing import Any, Callable, Dict, Generic, Sequence, TypeVar, Union

from fastapi import Depends
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql._typing import _DMLColumnArgument  # noqa:WPS436,WPS450

from snowfall.project.pss.service.pss_api_v2.db.db import get_db

REPOSITORY_MODEL = TypeVar("REPOSITORY_MODEL")


class Repository(Generic[REPOSITORY_MODEL]):  # noqa:WPS214
    def __init__(self, db: async_sessionmaker[AsyncSession]):
        self._db = db

    @classmethod
    def factory(
        cls,
        repository_model: REPOSITORY_MODEL,
    ) -> Callable[[async_sessionmaker[AsyncSession]], "Repository[REPOSITORY_MODEL]"]:
        def constructor(
            db: async_sessionmaker[AsyncSession] = Depends(get_db),
        ) -> "Repository[REPOSITORY_MODEL]":
            return cls[repository_model](db)  # type: ignore[index]

        return constructor

    async def list_all(self) -> Sequence[REPOSITORY_MODEL]:
        async with self._db() as session:
            statement = select(self._type)
            res = await session.execute(statement)
            return res.scalars().all()

    async def get_one_by_filter(
        self,
        filter_criteria: Sequence[ColumnElement[bool]],
    ) -> REPOSITORY_MODEL | None:
        async with self._db() as session:
            statement = select(self._type).filter(*filter_criteria)
            res = await session.execute(statement)
            return res.scalars().first()

    async def get_all_by_filter(
        self,
        filter_criteria: Sequence[ColumnElement[bool]],
    ) -> Sequence[REPOSITORY_MODEL]:
        async with self._db() as session:
            statement = select(self._type).filter(*filter_criteria)
            res = await session.execute(statement)
            return res.scalars().all()

    async def update_by_filter(
        self,
        filter_criteria: Sequence[ColumnElement[bool]],
        values_to_update: Union[  # noqa:WPS320,SF20
            Dict[_DMLColumnArgument, Any],  # noqa:SF20
            Sequence[Any],
        ],
    ) -> None:
        async with self._db().begin() as transaction:
            statement = (
                update(self._type).values(values_to_update).where(*filter_criteria)
            )
            await transaction.session.execute(statement)

    async def insert(self, to_insert: REPOSITORY_MODEL) -> None:
        async with self._db().begin() as transaction:
            transaction.session.add(to_insert)

    @property
    def _type(self) -> Any:
        """Return the type of model the Repository was instantiated with."""
        return self.__orig_class__.__args__[0]  # type: ignore[attr-defined]
