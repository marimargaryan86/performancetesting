import http
from typing import Optional

from openapi_core.exceptions import OpenAPIError
from starlette import exceptions, requests, responses

from snowfall.junction.client_api import models


async def _error_response_from_status(
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


async def error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.JSONResponse:
    if isinstance(exc, exceptions.HTTPException):
        return await exception_handler(request, exc)

    return await _error_response_from_status(http.HTTPStatus.INTERNAL_SERVER_ERROR)


async def exception_handler(
    request: requests.Request,
    exc: exceptions.HTTPException,
) -> responses.JSONResponse:
    status = http.HTTPStatus(exc.status_code or http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return await _error_response_from_status(status)


async def validation_error_handler(
    request: requests.Request,
    exc: OpenAPIError,
) -> responses.JSONResponse:
    return await _error_response_from_status(http.HTTPStatus.BAD_REQUEST, str(exc))
