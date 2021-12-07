import json
from collections.abc import AsyncIterable

import openapi_core
from openapi_core.exceptions import OpenAPIError
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator
from starlette import requests, responses
from werkzeug.datastructures import Headers

from snowfall.junction.client_api import handlers, loaders


async def _read_bytes(generator: AsyncIterable[bytes]) -> bytes:
    return b"".join([chunk async for chunk in generator])


async def _resolve_streaming_response(
    response: responses.StreamingResponse,
) -> responses.Response:
    body = await _read_bytes(response.body_iterator)

    return responses.Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type or "application/vnd.api+json",
        background=response.background,
    )


async def resolve_response(response: responses.Response) -> responses.Response:
    if isinstance(response, responses.StreamingResponse):
        return await _resolve_streaming_response(response)

    return response


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

    async def validate(
        self,
        request: requests.Request,
        response: responses.Response,
    ) -> responses.Response:
        try:
            openapi_request = await self._validate_request(request)
        except OpenAPIError as err:
            return await handlers.validation_error_handler(request, err)

        return await self._validate_response(openapi_request, response)

    async def _validate_request(self, request: requests.Request) -> OpenAPIRequest:
        openapi_request = await request_to_openapi(request)
        validation_result = self._request_validator.validate(openapi_request)
        validation_result.raise_for_errors()

        return openapi_request

    async def _validate_response(
        self,
        openapi_request: OpenAPIRequest,
        response: responses.Response,
    ) -> responses.Response:
        resolved_response = await resolve_response(response)
        openapi_response = await response_to_openapi(resolved_response)
        validation_result = self._response_validator.validate(
            openapi_request,
            openapi_response,
        )
        validation_result.raise_for_errors()

        return resolved_response
