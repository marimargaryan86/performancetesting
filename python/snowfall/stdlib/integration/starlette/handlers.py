import http

from openapi_core.validation.schemas import exceptions as validation_exceptions
from starlette import exceptions, requests, responses, status

from snowfall.stdlib.integration.starlette import models, validation


def error_response_from_status(
    status_code: int,
    description: str | None = None,
) -> responses.Response:
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
) -> responses.Response:
    return error_response_from_status(status.HTTP_401_UNAUTHORIZED)


def not_found_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    return error_response_from_status(status.HTTP_404_NOT_FOUND)


def service_unavailable_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    return error_response_from_status(status.HTTP_503_SERVICE_UNAVAILABLE)


def unprocessable_entity_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    status_code_obj = http.HTTPStatus(status.HTTP_422_UNPROCESSABLE_ENTITY)
    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status=str(int(status_code_obj)),
                    title=status_code_obj.phrase,
                    detail=str(exc),
                ),
            ],
        ),
        status_code=int(status_code_obj),
    )


async def cursor_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    status_code_obj = http.HTTPStatus(status.HTTP_400_BAD_REQUEST)

    return models.JsonApiResponse(
        models.Body(
            errors=[
                models.Error(
                    status=str(int(status_code_obj)),
                    title=status_code_obj.phrase,
                    detail="Invalid cursor",
                    source=models.ErrorSourceParameter(
                        parameter="page[cursor]",
                    ),
                ),
            ],
        ),
        status_code=int(status_code_obj),
    )


async def client_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    status_code = status.HTTP_400_BAD_REQUEST

    if isinstance(exc, exceptions.HTTPException) and exc.status_code:
        status_code = exc.status_code

    return error_response_from_status(status_code)


async def server_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, exceptions.HTTPException) and exc.status_code:
        status_code = exc.status_code

    return error_response_from_status(status_code)


async def validation_error_handler(
    request: requests.Request,
    exc: validation_exceptions.InvalidSchemaValue,
) -> responses.Response:
    return models.JsonApiResponse(
        models.Body(
            errors=validation.invalid_schema_value_to_errors(
                exc=exc,
                status_code=status.HTTP_400_BAD_REQUEST,
            ),
        ),
        status_code=http.HTTPStatus.BAD_REQUEST,
    )


async def forbidden_error_handler(
    request: requests.Request,
    exc: Exception,
) -> responses.Response:
    return error_response_from_status(status.HTTP_403_FORBIDDEN)
