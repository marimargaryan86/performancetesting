from typing import Any, Callable, Generic, TypeVar

from fastapi import Depends
from sqlalchemy.orm import Session

from snowfall.project.pss.service.pss_api_v2.db.db import get_db

REPOSITORY_MODEL = TypeVar("REPOSITORY_MODEL")


class Repository(Generic[REPOSITORY_MODEL]):
    def __init__(self, db: Session):
        self._db = db

    @classmethod
    def factory(
        cls,
        repository_model: REPOSITORY_MODEL,
    ) -> Callable[[Session], "Repository[REPOSITORY_MODEL]"]:
        def constructor(
            db: Session = Depends(get_db),
        ) -> "Repository[REPOSITORY_MODEL]":
            return cls[repository_model](db)  # type: ignore[index]

        return constructor

    def list_all(self) -> list[REPOSITORY_MODEL]:
        return self._db.query(self._type).all()

    @property
    def _type(self) -> Any:
        """Return the type of model the Repository was instantiated with."""
        return self.__orig_class__.__args__[0]  # type: ignore[attr-defined]
