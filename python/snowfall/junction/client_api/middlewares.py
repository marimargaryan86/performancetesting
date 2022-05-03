import http
from collections.abc import AsyncIterable
from typing import Awaitable, Callable, Container, Optional

import sentry_sdk
from openapi_core.exceptions import OpenAPIError
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.validation.request.datatypes import OpenAPIRequest
from starlette import applications, exceptions, requests, responses, status, types
from starlette.middleware import base

from snowfall.junction.client_api import handlers, validation


class RequestWithBody(requests.Request):
    def __init__(self, scope: types.Scope, body: bytes) -> None:
        super().__init__(scope, self._receive)
        self._body = body
        self._body_returned = False

    async def _receive(self) -> types.Message:
        if self._body_returned:
            return {"type": "http.disconnect"}

        self._body_returned = True
        return {"type": "http.request", "body": self._body, "more_body": False}


async def resolve_request(request: requests.Request) -> requests.Request:
    return RequestWithBody(request.scope, await request.body())


async def resolve_response(response: responses.Response) -> responses.Response:
    if isinstance(response, responses.StreamingResponse):
        return await _resolve_streaming_response(response)

    return response


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


async def _read_bytes(generator: AsyncIterable[bytes]) -> bytes:
    return b"".join([chunk async for chunk in generator])


class RequestIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        response = await call_next(request)
        transaction = sentry_sdk.Hub.current.scope.transaction

        if transaction:
            response.headers["X-Request-Id"] = transaction.trace_id

        return response


class ValidationMiddleware(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        validator: validation.Validator,
        excluded_status_codes: Optional[Container[http.HTTPStatus]] = None,
    ):
        super().__init__(app)
        self._validator = validator
        self._excluded_status_codes = excluded_status_codes or []

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        resolved_request = await resolve_request(request)
        openapi_request = await validation.request_to_openapi(resolved_request)

        try:
            openapi_result = await self._validator.validate_request(openapi_request)
        except PathNotFound:
            raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        except OpenAPIError as err:
            return await handlers.validation_error_handler(resolved_request, err)

        resolved_request.scope["jwt"] = openapi_result.security.get("jwt")
        resolved_request.scope["query_string"] = openapi_result.parameters.query

        return await self._dispatch(call_next, openapi_request, resolved_request)

    async def _dispatch(
        self,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
        openapi_request: OpenAPIRequest,
        resolved_request: requests.Request,
    ) -> responses.Response:
        response = await call_next(resolved_request)
        resolved_response = await resolve_response(response)

        if resolved_response.status_code in self._excluded_status_codes:
            return resolved_response

        openapi_response = await validation.response_to_openapi(resolved_response)
        await self._validator.validate_response(openapi_request, openapi_response)

        return resolved_response
