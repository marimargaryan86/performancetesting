from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from snowfall.project.pss.service.api.db.db import get_db
from snowfall.project.pss.service.api.db.models.accounts import Account


class AccountsRepository(object):
    def __init__(self, db: Session = Depends(get_db)):
        self._db = db

    def list_accounts(self) -> list[Any]:
        return self._db.query(Account).all()
