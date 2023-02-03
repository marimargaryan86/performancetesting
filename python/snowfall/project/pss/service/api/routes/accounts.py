from typing import List, Sequence

from fastapi import Depends
from fastapi.routing import APIRouter

from snowfall.project.pss.service.api.db.models.accounts import Account
from snowfall.project.pss.service.api.db.repository.accounts import AccountsRepository
from snowfall.project.pss.service.api.schemas.accounts import AccountResponseSchema

router = APIRouter()


@router.get("", response_model=List[AccountResponseSchema])
def read_accounts(
    account_repository: AccountsRepository = Depends(AccountsRepository),
) -> Sequence[Account]:
    return account_repository.list_accounts()
