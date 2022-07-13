from typing import Any, Awaitable, Callable, Container, Mapping, Optional, cast

import sentry_sdk
import structlog
from openapi_core.exceptions import OpenAPIError
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.validation.exceptions import InvalidSecurity
from openapi_core.validation.request.datatypes import OpenAPIRequest
from starlette import applications, exceptions, requests, responses, status, types
from starlette.middleware import base

from snowfall.stdlib.integration.starlette import handlers, request_helpers, validation
from snowfall.stdlib.logging import stdout


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


async def _read_bytes(generator: responses.AsyncContentStream) -> responses.Content:
    list_ = [chunk async for chunk in generator]

    if not list_:
        return ""

    if all(isinstance(list_item, bytes) for list_item in list_):
        return b"".join(cast(list[bytes], list_))

    if all(isinstance(list_item, str) for list_item in list_):
        return "".join(cast(list[str], list_))

    raise RuntimeError


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
        excluded_status_codes: Optional[Container[int]] = None,
    ):
        super().__init__(app)
        self._logger = structlog.get_logger(__name__)
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
        except OpenAPIError as err:
            return await self._handle_validation_error(resolved_request, err)

        if openapi_result.body:
            resolved_request.scope["body"] = request_helpers.flatten_request_body(
                cast(Mapping[str, Any], openapi_result.body),
            )

        resolved_request.scope["query_string"] = openapi_result.parameters.query
        resolved_request.scope["security"] = openapi_result.security

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

        try:
            await self._validator.validate_response(openapi_request, openapi_response)
        except InvalidSchemaValue as err:
            return await self._handle_response_schema_error(resolved_request, err)

        return resolved_response

    async def _handle_response_schema_error(
        self,
        request: requests.Request,
        exc: InvalidSchemaValue,
    ) -> responses.JSONResponse:
        with stdout.context_binding(
            errors=[
                error.dict()
                for error in validation.invalid_schema_value_to_errors(
                    exc=exc,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            ],
            body=exc.value,
        ):
            self._logger.error("Response body does not validate against schema")

        return await handlers.server_error_handler(request, exc)

    async def _handle_validation_error(
        self,
        request: requests.Request,
        err: OpenAPIError,
    ) -> responses.JSONResponse:
        if isinstance(err, PathNotFound):
            return await handlers.server_error_handler(
                request,
                exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND),
            )

        if isinstance(err, InvalidSchemaValue):
            return await handlers.validation_error_handler(request, err)

        if isinstance(err, InvalidSecurity):
            return await handlers.server_error_handler(
                request,
                exceptions.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED),
            )

        return await handlers.server_error_handler(
            request,
            exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST),
        )
