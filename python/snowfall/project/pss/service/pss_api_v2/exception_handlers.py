from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from snowfall.project.pss.service.pss_api_v2 import messages
from snowfall.project.pss.service.pss_api_v2.exceptions import AccountNotFoundError
from snowfall.project.pss.service.pss_api_v2.responses import ErrorResponse


def add_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AccountNotFoundError, account_not_found_exception_handler)


async def account_not_found_exception_handler(
    request: Request,
    exc: AccountNotFoundError,
) -> JSONResponse:
    return ErrorResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=messages.ACCOUNT_NOT_FOUND,
    )
