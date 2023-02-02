from typing import Sequence

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from snowfall.project.pss.service.api.db import db
from snowfall.project.pss.service.api.db.models.countries import Country


class CountriesService(object):
    def __init__(self, db_session: Session = Depends(db.get_db)) -> None:
        self._db = db_session

    def get_all(self) -> Sequence[Country]:
        return self._db.execute(select(Country)).scalars().all()
