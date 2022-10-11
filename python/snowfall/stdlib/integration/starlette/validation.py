import dataclasses
from typing import Optional, cast

import jsonschema
import openapi_core
import openapi_schema_validator
import rapidjson
from openapi_core.deserializing.media_types.factories import (
    MediaTypeDeserializersFactory,
)
from openapi_core.unmarshalling.schemas import enums
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.unmarshalling.schemas.factories import SchemaUnmarshallersFactory
from openapi_core.validation.request import protocols as request_protocols
from openapi_core.validation.request.datatypes import (
    RequestParameters,
    RequestValidationResult,
)
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response import protocols as response_protocols
from openapi_core.validation.response.validators import ResponseValidator
from starlette import requests, responses
from werkzeug.datastructures import Headers

from snowfall.stdlib.integration.starlette import formatters, models


@dataclasses.dataclass(frozen=True)
class OpenAPIRequest(object):
    host_url: str
    path: str
    method: str
    body: Optional[str]
    mimetype: str
    parameters: RequestParameters = dataclasses.field(  # noqa: WPS110
        default_factory=RequestParameters,
    )


@dataclasses.dataclass(frozen=True)
class OpenAPIResponse(object):
    data: str  # noqa: WPS110
    status_code: int
    mimetype: str
    headers: Headers = dataclasses.field(default_factory=Headers)


async def request_to_openapi(request: requests.Request) -> request_protocols.Request:
    return cast(
        request_protocols.Request,
        OpenAPIRequest(
            host_url="{scheme}://{hostname}".format(
                scheme=request.url.scheme,
                hostname=request.url.hostname,
            ),
            path=request.url.path,
            method=request.method.lower(),
            parameters=RequestParameters(
                query=request.query_params,
                header=Headers(dict(request.headers)),
                cookie=request.cookies,
            ),
            body=(await request.body()).decode("utf-8"),
            mimetype=request.headers.get(
                "Content-Type",
                request.headers.get("Accept", ""),
            ),
        ),
    )


async def response_to_openapi(
    response: responses.Response,
) -> response_protocols.Response:
    return cast(
        response_protocols.Response,
        OpenAPIResponse(
            data=response.body.decode("utf-8"),
            mimetype=str(response.media_type) if response.media_type else "",
            status_code=response.status_code,
            headers=Headers(dict(response.headers)),
        ),
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
            self._spec = openapi_core.Spec.create(
                rapidjson.load(spec_file),
                url="file://{0}".format(spec_path),
            )

        deserializer = {"application/vnd.api+json": rapidjson.loads}

        self._request_validator = RequestValidator(
            schema_unmarshallers_factory=SchemaUnmarshallersFactory(
                schema_validator_class=openapi_schema_validator.OAS30Validator,
                custom_formatters=formatters.custom_formatters(),
                context=enums.UnmarshalContext.REQUEST,
            ),
            media_type_deserializers_factory=MediaTypeDeserializersFactory(
                custom_deserializers=deserializer,
            ),
        )
        self._response_validator = ResponseValidator(
            schema_unmarshallers_factory=SchemaUnmarshallersFactory(
                schema_validator_class=openapi_schema_validator.OAS30Validator,
                custom_formatters=formatters.custom_formatters(),
                context=enums.UnmarshalContext.RESPONSE,
            ),
            media_type_deserializers_factory=MediaTypeDeserializersFactory(
                custom_deserializers=deserializer,
            ),
        )

    async def validate_request(
        self,
        request: request_protocols.Request,
    ) -> RequestValidationResult:
        validation_result = self._request_validator.validate(
            spec=self._spec,
            request=request,
        )

        validation_result.raise_for_errors()

        return validation_result

    async def validate_response(
        self,
        request: request_protocols.Request,
        response: response_protocols.Response,
    ) -> None:
        validation_result = self._response_validator.validate(
            spec=self._spec,
            request=request,
            response=response,
        )
        validation_result.raise_for_errors()
