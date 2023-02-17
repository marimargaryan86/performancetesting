from typing import Any, Callable, Generic, Sequence, TypeVar

from fastapi import Depends
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from snowfall.project.pss.service.pss_api_v2.db.db import get_db

REPOSITORY_MODEL = TypeVar("REPOSITORY_MODEL")


class Repository(Generic[REPOSITORY_MODEL]):
    def __init__(self, db: AsyncSession):
        self._db = db

    @classmethod
    def factory(
        cls,
        repository_model: REPOSITORY_MODEL,
    ) -> Callable[[AsyncSession], "Repository[REPOSITORY_MODEL]"]:
        def constructor(
            db: AsyncSession = Depends(get_db),
        ) -> "Repository[REPOSITORY_MODEL]":
            return cls[repository_model](db)  # type: ignore[index]

        return constructor

    async def list_all(self) -> Sequence[REPOSITORY_MODEL]:
        statement = select(self._type)
        res = await self._db.execute(statement)
        return res.scalars().all()

    async def get_one_by_filter(
        self,
        filter_criteria: Sequence[ColumnElement[bool]],
    ) -> REPOSITORY_MODEL | None:
        statement = select(self._type).filter(*filter_criteria)
        res = await self._db.execute(statement)
        return res.scalars().first()

    @property
    def _type(self) -> Any:
        """Return the type of model the Repository was instantiated with."""
        return self.__orig_class__.__args__[0]  # type: ignore[attr-defined]
