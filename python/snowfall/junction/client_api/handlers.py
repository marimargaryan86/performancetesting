import http
from typing import Optional

from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from starlette import exceptions, requests, responses

from snowfall.junction.client_api import models


def _error_response_from_status(
    status: http.HTTPStatus,
    description: Optional[str] = None,
) -> responses.JSONResponse:
    if not description:
        description = status.description

    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status=str(int(status)),
                    title=status.phrase,
                    detail=description,
                ),
            ],
        ),
        status_code=status,
    )


def auth_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    return _error_response_from_status(http.HTTPStatus.UNAUTHORIZED)


async def error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    if isinstance(exc, exceptions.HTTPException):
        return await exception_handler(request, exc)

    return _error_response_from_status(http.HTTPStatus.INTERNAL_SERVER_ERROR)


async def exception_handler(
    request: requests.Request,
    exc: exceptions.HTTPException,
) -> responses.JSONResponse:
    status = http.HTTPStatus(exc.status_code or http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return _error_response_from_status(status)


async def validation_error_handler(
    request: requests.Request,
    exc: InvalidSchemaValue,
) -> responses.JSONResponse:
    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status=str(int(http.HTTPStatus.BAD_REQUEST)),
                    code=error.validator,
                    detail=error.message,
                    source=models.ErrorSource(
                        pointer="/{0}".format(
                            "/".join([str(path) for path in error.absolute_path]),
                        ),
                    ),
                )
                for error in exc.schema_errors
            ],
        ),
        status_code=http.HTTPStatus.BAD_REQUEST,
    )
