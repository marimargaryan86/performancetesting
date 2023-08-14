import dataclasses
import pathlib
from typing import cast

import jsonschema
import orjson
from openapi_core import protocols, shortcuts, spec
from openapi_core.unmarshalling.request import datatypes as request_datatypes
from openapi_core.unmarshalling.response import datatypes as response_datatypes
from openapi_core.validation.request.datatypes import RequestParameters
from openapi_core.validation.schemas import exceptions as validation_exceptions
from starlette import requests, responses
from werkzeug.datastructures import Headers

from snowfall.stdlib.integration.starlette import formatters, models


@dataclasses.dataclass(frozen=True)
class OpenAPIRequest(object):
    host_url: str
    path: str
    method: str
    body: str | None
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


async def request_to_openapi(request: requests.Request) -> protocols.Request:
    return cast(
        protocols.Request,
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
) -> protocols.Response:
    return cast(
        protocols.Response,
        OpenAPIResponse(
            data=response.body.decode("utf-8"),
            mimetype=str(response.media_type) if response.media_type else "",
            status_code=response.status_code,
            headers=Headers(dict(response.headers)),
        ),
    )


def invalid_schema_value_to_errors(
    exc: validation_exceptions.InvalidSchemaValue,
    status_code: int,
) -> list[models.Error]:
    return [
        models.Error(
            status=str(status_code),
            code=str(error.validator),
            detail=error.message,
            source=models.ErrorSourcePointer(
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
        spec_path: pathlib.Path,
    ):
        with spec_path.open() as spec_file:
            self._spec = spec.Spec.from_dict(
                orjson.loads(spec_file.read()),
                spec_url="file://{0}".format(spec_path),
            )

        self._format_unmarshallers = formatters.format_unmarshallers()
        self._format_validators = formatters.format_validators()
        self._media_type_deserializers = {
            "application/vnd.api+json": orjson.loads,
        }

    async def validate_request(
        self,
        request: protocols.Request,
    ) -> request_datatypes.RequestUnmarshalResult:
        return shortcuts.unmarshal_request(
            request=request,
            spec=self._spec,
            extra_media_type_deserializers=self._media_type_deserializers,
            extra_format_validators=self._format_validators,
            extra_format_unmarshallers=self._format_unmarshallers,
        )

    async def validate_response(
        self,
        request: protocols.Request,
        response: protocols.Response,
    ) -> response_datatypes.ResponseUnmarshalResult:
        return shortcuts.unmarshal_response(
            request=request,
            response=response,
            spec=self._spec,
            extra_media_type_deserializers=self._media_type_deserializers,
            extra_format_validators=self._format_validators,
            extra_format_unmarshallers=self._format_unmarshallers,
        )
