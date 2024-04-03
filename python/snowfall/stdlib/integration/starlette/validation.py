import asyncio
import http
import pathlib
from collections.abc import Iterable
from types import MappingProxyType

import orjson
from jsonschema import exceptions as jsonschema_exceptions
from openapi_core import OpenAPI, configurations, exceptions, protocols
from openapi_core.contrib.starlette import (
    StarletteOpenAPIRequest,
    StarletteOpenAPIResponse,
    handlers,
)
from openapi_core.templating.security import exceptions as security_exceptions
from openapi_core.unmarshalling.request import datatypes as request_datatypes
from openapi_core.unmarshalling.response import datatypes as response_datatypes
from openapi_core.validation.schemas import exceptions as schema_exceptions
from sentry_sdk import tracing
from starlette import requests, responses

from snowfall.stdlib import string
from snowfall.stdlib.integration.openapi_core import formats
from snowfall.stdlib.integration.starlette import models

_status_codes: MappingProxyType[type[BaseException], int] = MappingProxyType({
    **handlers.StarletteOpenAPIErrorsHandler.OPENAPI_ERROR_STATUS,
    security_exceptions.SecurityNotFound: 401,
})


async def request_to_openapi(request: requests.Request) -> protocols.Request:
    return StarletteOpenAPIRequest(request=request, body=await request.body())


async def response_to_openapi(
    response: responses.Response,
) -> protocols.Response:
    return StarletteOpenAPIResponse(response=response, data=response.body)


def openapi_errors_to_errors(
    errors: Iterable[exceptions.OpenAPIError],
) -> Iterable[models.Error]:
    for error in errors:
        actual_error: BaseException = error

        if error.__cause__ is not None:
            actual_error = error.__cause__

        if isinstance(actual_error, schema_exceptions.InvalidSchemaValue):
            yield from jsonschema_errors_to_errors(actual_error.schema_errors)
        else:
            status_code_obj = http.HTTPStatus(
                _status_codes.get(
                    actual_error.__class__,
                    int(http.HTTPStatus.BAD_REQUEST),
                ),
            )

            yield models.Error(
                status=str(int(status_code_obj)),
                title=status_code_obj.phrase,
                code=string.to_snake(type(actual_error).__name__).upper(),
                detail=status_code_obj.description,
            )


def jsonschema_errors_to_errors(
    errors: Iterable[Exception],
) -> Iterable[models.Error]:
    status_code_obj = http.HTTPStatus.BAD_REQUEST

    for error in errors:
        if not isinstance(error, jsonschema_exceptions.ValidationError):
            raise NotImplementedError

        yield models.Error(
            status=str(int(status_code_obj)),
            title=status_code_obj.phrase,
            code=string.to_snake(type(error).__name__).upper(),
            detail=error.message,
            source=models.ErrorSourcePointer(
                pointer="/{0}".format(
                    "/".join([str(path) for path in error.absolute_path]),
                ),
            ),
        )


class Validator:
    def __init__(
        self,
        spec_path: pathlib.Path,
    ):
        self._spec = OpenAPI.from_path(
            spec_path.resolve(strict=True),
            config=configurations.Config(
                spec_base_uri="file://{0}".format(spec_path.resolve(strict=True)),
                extra_media_type_deserializers={
                    "application/vnd.api+json": orjson.loads,
                },
                extra_format_unmarshallers=formats.format_unmarshallers(),
                extra_format_validators=formats.format_validators(),
            ),
        )

    @tracing.trace
    async def validate_request(
        self,
        request: protocols.Request,
    ) -> request_datatypes.RequestUnmarshalResult:
        loop = asyncio.get_running_loop()

        def wrapper() -> request_datatypes.RequestUnmarshalResult:
            return self._spec.unmarshal_request(request=request)

        return await loop.run_in_executor(None, wrapper)

    @tracing.trace
    async def validate_response(
        self,
        request: protocols.Request,
        response: protocols.Response,
    ) -> response_datatypes.ResponseUnmarshalResult:
        loop = asyncio.get_running_loop()

        def wrapper() -> response_datatypes.ResponseUnmarshalResult:
            return self._spec.unmarshal_response(request=request, response=response)

        return await loop.run_in_executor(None, wrapper)
