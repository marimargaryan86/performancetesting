import json
from typing import Any

import openapi_core
from furl import furl
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

from snowfall.filesystem import loaders


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
    )


class UriFormatter(object):
    def validate(self, potential_url: Any) -> bool:
        try:
            self.unmarshal(potential_url)
        except ValueError:
            return False

        return True

    def unmarshal(self, url: Any) -> furl:
        return furl(url)


class Validator(object):
    def __init__(self, spec_path: str, loader: loaders.Loader):
        spec_dict = loader.load(spec_path)
        spec = openapi_core.create_spec(spec_dict)
        deserializer = {"application/vnd.api+json": json.loads}
        formatter = {"uri": UriFormatter()}
        self._request_validator = RequestValidator(
            spec,
            custom_formatters=formatter,
            custom_media_type_deserializers=deserializer,
        )
        self._response_validator = ResponseValidator(
            spec,
            custom_formatters=formatter,
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
