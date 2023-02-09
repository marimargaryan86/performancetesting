from typing import List, Sequence

from fastapi import Depends
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import (
    AccountResponseSchema,
)
from snowfall.project.pss.service.pss_api_v2.services.accounts import AccountsService

router = APIRouter()


@router.get("", response_model=List[AccountResponseSchema])
async def read_accounts(
    account_service: AccountsService = Depends(AccountsService),
) -> Sequence[Account]:
    return await account_service.get_all()
