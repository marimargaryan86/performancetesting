from typing import List, Sequence

import bcrypt
from fastapi import Depends, status
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.db.models.accounts import Account
from snowfall.project.pss.service.pss_api_v2.responses import ErrorMessage
from snowfall.project.pss.service.pss_api_v2.schemas import openapi_responses
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import (
    AccountDetailedResponseSchema,
    AccountLoginSchema,
    AccountResponseSchema,
)
from snowfall.project.pss.service.pss_api_v2.services.accounts import AccountsService

router = APIRouter()


@router.get("", response_model=List[AccountResponseSchema])
async def read_accounts(
    account_service: AccountsService = Depends(AccountsService),
) -> Sequence[Account]:
    return await account_service.get_all()


@router.post(
    "/login",
    response_model=AccountDetailedResponseSchema,
    responses=openapi_responses.login_responses,
)
async def account_login(
    account_data: AccountLoginSchema,
    account_service: AccountsService = Depends(AccountsService),
) -> Account | ErrorMessage:
    account = await account_service.get_account_by_email(account_data.email)

    if account is None:
        return ErrorMessage(
            status_code=status.HTTP_404_NOT_FOUND,
            message=messages.ACCOUNT_NOT_FOUND,
        )

    if not account.active:
        return ErrorMessage(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_NOT_ACTIVE,
        )

    if not bcrypt.checkpw(account_data.password.encode(), account.password.encode()):
        return ErrorMessage(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_PASSWORD_DONT_MATCH,
        )

    return account
