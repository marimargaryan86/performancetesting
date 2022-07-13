import http
from typing import Optional

from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from starlette import exceptions, requests, responses, status

from snowfall.stdlib.integration.starlette import models, validation


def error_response_from_status(
    status_code: int,
    description: Optional[str] = None,
) -> responses.JSONResponse:
    status_code_obj = http.HTTPStatus(status_code)

    if not description:
        description = status_code_obj.description

    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status=str(int(status_code_obj)),
                    title=status_code_obj.phrase,
                    detail=description,
                ),
            ],
        ),
        status_code=int(status_code_obj),
    )


def auth_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    return error_response_from_status(status.HTTP_401_UNAUTHORIZED)


async def client_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    status_code = status.BAD_REQUEST

    if isinstance(exc, exceptions.HTTPException) and exc.status_code:
        status_code = exc.status_code

    return error_response_from_status(status_code)


async def server_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, exceptions.HTTPException) and exc.status_code:
        status_code = exc.status_code

    return error_response_from_status(status_code)


async def validation_error_handler(
    request: requests.Request,
    exc: InvalidSchemaValue,
) -> responses.JSONResponse:
    return models.JsonApiResponse(
        models.Body(
            errors=validation.invalid_schema_value_to_errors(
                exc=exc,
                status_code=status.HTTP_400_BAD_REQUEST,
            ),
        ),
        status_code=http.HTTPStatus.BAD_REQUEST,
    )
