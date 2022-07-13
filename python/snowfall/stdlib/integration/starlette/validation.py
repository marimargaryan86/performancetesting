from typing import cast

import jsonschema
import openapi_core
import rapidjson
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
    RequestValidationResult,
)
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator
from starlette import requests, responses
from werkzeug.datastructures import Headers

from snowfall.stdlib.integration.starlette import formatters, models


async def request_to_openapi(request: requests.Request) -> OpenAPIRequest:
    return OpenAPIRequest(
        full_url_pattern="{scheme}://{hostname}{path}".format(
            scheme=request.url.scheme,
            hostname=request.url.hostname,
            path=request.url.path,
        ),
        method=request.method.lower(),
        parameters=RequestParameters(
            query=request.query_params,
            header=Headers(dict(request.headers)),
            cookie=request.cookies,
        ),
        body=await request.body(),
        mimetype=request.headers.get("Content-Type", request.headers.get("Accept")),
    )


async def response_to_openapi(response: responses.Response) -> OpenAPIResponse:
    return OpenAPIResponse(
        data=response.body.decode("utf-8"),
        mimetype=response.media_type,
        status_code=response.status_code,
        headers=Headers(dict(response.headers)),
    )


def invalid_schema_value_to_errors(
    exc: InvalidSchemaValue,
    status_code: int,
) -> list[models.Error]:
    return [
        models.Error(
            status=str(status_code),
            code=error.validator,
            detail=error.message,
            source=models.ErrorSource(
                pointer="/{0}".format(
                    "/".join([str(path) for path in error.absolute_path]),
                ),
            ),
        )
        for error in cast(list[jsonschema.ValidationError], exc.schema_errors)
    ]


class Validator(object):
    def __init__(
        self,
        spec_path: str,
    ):
        with open(spec_path) as spec_file:
            spec = openapi_core.OpenAPISpec.create(
                rapidjson.load(spec_file),
                url="file://{0}".format(spec_path),
            )
            deserializer = {"application/vnd.api+json": rapidjson.loads}
            self._request_validator = RequestValidator(
                spec,
                custom_formatters=formatters.custom_formatters(),
                custom_media_type_deserializers=deserializer,
            )
            self._response_validator = ResponseValidator(
                spec,
                custom_formatters=formatters.custom_formatters(),
                custom_media_type_deserializers=deserializer,
            )

    async def validate_request(
        self,
        request: OpenAPIRequest,
    ) -> RequestValidationResult:
        validation_result = self._request_validator.validate(request)
        validation_result.raise_for_errors()

        return validation_result

    async def validate_response(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> None:
        validation_result = self._response_validator.validate(request, response)
        validation_result.raise_for_errors()
