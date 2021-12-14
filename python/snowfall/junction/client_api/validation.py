import json

import openapi_core
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator
from starlette import requests, responses
from werkzeug.datastructures import Headers

from snowfall.junction.client_api import loaders


async def request_to_openapi(request: requests.Request) -> OpenAPIRequest:
    return OpenAPIRequest(
        full_url_pattern=str(request.url),
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


class Validator(object):
    def __init__(self, spec_path: str, loader: loaders.Loader):
        spec_dict = loader.load(spec_path)
        spec = openapi_core.create_spec(spec_dict)
        deserializer = {"application/vnd.api+json": json.loads}
        self._request_validator = RequestValidator(
            spec,
            custom_media_type_deserializers=deserializer,
        )
        self._response_validator = ResponseValidator(
            spec,
            custom_media_type_deserializers=deserializer,
        )

    async def validate_request(self, request: OpenAPIRequest) -> None:
        validation_result = self._request_validator.validate(request)
        validation_result.raise_for_errors()

    async def validate_response(
        self,
        request: OpenAPIRequest,
        response: OpenAPIResponse,
    ) -> None:
        validation_result = self._response_validator.validate(request, response)
        validation_result.raise_for_errors()
