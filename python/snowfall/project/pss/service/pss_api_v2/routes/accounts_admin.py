import bcrypt
from fastapi import Depends, status
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.responses import (
    ErrorResponse,
    SuccessResponse,
)
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import (
    AccountLoginSchema,
    AdminAccountDetailedResponseSchema,
)
from snowfall.project.pss.service.pss_api_v2.schemas.responses import ResponseSchema
from snowfall.project.pss.service.pss_api_v2.services.accounts import (
    AccountsService,
    has_admin_permissions,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=ResponseSchema[AdminAccountDetailedResponseSchema],
)
async def admin_login(
    account_data: AccountLoginSchema,
    account_service: AccountsService = Depends(AccountsService),
) -> SuccessResponse | ErrorResponse:
    account = await account_service.get_account_by_email(account_data.email)

    if account is None:
        return ErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message=messages.ACCOUNT_NOT_FOUND,
        )

    if not bcrypt.checkpw(account_data.password.encode(), account.password.encode()):
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_PASSWORD_DONT_MATCH,
        )

    if not account.active:
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_NOT_ACTIVE,
        )

    if not has_admin_permissions(account=account):
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_NOT_ALLOWED,
        )

    return SuccessResponse(
        status_code=status.HTTP_200_OK,
        data=AdminAccountDetailedResponseSchema.from_orm(account).dict(),
    )
