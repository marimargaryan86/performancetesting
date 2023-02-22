from typing import List

import bcrypt
from fastapi import Depends, status
from fastapi.routing import APIRouter

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.responses import (
    ErrorResponse,
    SuccessResponse,
)
from snowfall.project.pss.service.pss_api_v2.schemas import openapi_responses
from snowfall.project.pss.service.pss_api_v2.schemas.accounts import (
    AccountDetailedResponseSchema,
    AccountForgotPasswordSchema,
    AccountLoginSchema,
    AccountResetPasswordSchema,
    AccountResponseSchema,
)
from snowfall.project.pss.service.pss_api_v2.schemas.responses import ResponseSchema
from snowfall.project.pss.service.pss_api_v2.services.accounts import (
    AccountForgottenPasswordNotFoundError,
    AccountForgottenPasswordTokenAlreadyUsedError,
    AccountForgottenPasswordTokenExpiredError,
    AccountsService,
)

router = APIRouter()


@router.get("", response_model=ResponseSchema[List[AccountResponseSchema]])
async def read_accounts(
    account_service: AccountsService = Depends(AccountsService),
) -> SuccessResponse:
    accounts = await account_service.get_all()
    return SuccessResponse(
        status_code=status.HTTP_200_OK,
        data=[AccountResponseSchema.from_orm(account).dict() for account in accounts],
    )


@router.post(
    "/login",
    response_model=ResponseSchema[AccountDetailedResponseSchema],
    responses=openapi_responses.login_responses,
)
async def account_login(
    account_data: AccountLoginSchema,
    account_service: AccountsService = Depends(AccountsService),
) -> SuccessResponse | ErrorResponse:
    account = await account_service.get_account_by_email(account_data.email)

    if account is None:
        return ErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message=messages.ACCOUNT_NOT_FOUND,
        )

    if not account.active:
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_NOT_ACTIVE,
        )

    if not bcrypt.checkpw(account_data.password.encode(), account.password.encode()):
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_PASSWORD_DONT_MATCH,
        )

    return SuccessResponse(
        status_code=status.HTTP_200_OK,
        data=AccountDetailedResponseSchema.from_orm(account).dict(),
    )


@router.post(
    "/forgotpassword",
    response_model=ResponseSchema,
    responses=openapi_responses.forgot_password_responses,
)
async def forgot_password(
    account_forgot_password_data: AccountForgotPasswordSchema,
    account_service: AccountsService = Depends(AccountsService),
) -> SuccessResponse | ErrorResponse:
    account = await account_service.get_account_by_email(
        account_forgot_password_data.email,
    )

    if account is None:
        return ErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message=messages.ACCOUNT_NOT_FOUND,
        )

    await account_service.handle_forgotten_password(account)

    return SuccessResponse(status_code=status.HTTP_200_OK, data=None)


@router.post(
    "/resetpassword",
    response_model=ResponseSchema,
    responses=openapi_responses.reset_password_responses,
)
async def reset_password(
    account_reset_password_data: AccountResetPasswordSchema,
    account_service: AccountsService = Depends(AccountsService),
) -> SuccessResponse | ErrorResponse:
    try:
        await account_service.reset_password(
            token=account_reset_password_data.token,
            password=account_reset_password_data.password,
        )
    except AccountForgottenPasswordNotFoundError:
        return ErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message=messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_NOT_FOUND,
        )
    except AccountForgottenPasswordTokenAlreadyUsedError:
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_ALREADY_USED,
        )
    except AccountForgottenPasswordTokenExpiredError:
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=messages.ACCOUNT_FORGOTTEN_PASSWORD_TOKEN_EXPIRED,
        )
    return SuccessResponse(status_code=status.HTTP_200_OK, data=None)
