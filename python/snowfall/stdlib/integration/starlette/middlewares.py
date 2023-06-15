from collections.abc import Awaitable, Callable, Container
from typing import cast

import sentry_sdk
from openapi_core.exceptions import OpenAPIError
from openapi_core.templating.paths.exceptions import PathNotFound
from openapi_core.templating.security import exceptions as security_exceptions
from openapi_core.validation.request import protocols as request_protocols
from openapi_core.validation.schemas import exceptions as validation_exceptions
from starlette import applications, exceptions, requests, responses, status, types
from starlette.middleware import base

from snowfall.stdlib.integration.starlette import handlers, validation
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


class SecurityHeadersMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
        )

        return response


class ValidationMiddleware(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        validator: validation.Validator,
        excluded_status_codes: Container[int] | None = None,
        validate_response: bool = True,
    ):
        super().__init__(app)
        self._logger = stdout.get_logger()
        self._response_logger = stdout.get_logger()
        self._validator = validator
        self._excluded_status_codes = excluded_status_codes or []
        self._validate_response = validate_response

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

        resolved_request.scope["parsed_query_string"] = openapi_result.parameters.query
        resolved_request.scope["security"] = openapi_result.security

        return await self._dispatch(call_next, openapi_request, resolved_request)

    async def _dispatch(
        self,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
        openapi_request: request_protocols.Request,
        resolved_request: requests.Request,
    ) -> responses.Response:
        response = await call_next(resolved_request)

        if not self._validate_response:
            return response

        resolved_response = await resolve_response(response)

        if resolved_response.status_code in self._excluded_status_codes:
            return resolved_response

        openapi_response = await validation.response_to_openapi(resolved_response)

        try:
            await self._validator.validate_response(
                openapi_request,
                openapi_response,
            )
        except OpenAPIError as err:
            if isinstance(err.__cause__, validation_exceptions.InvalidSchemaValue):
                return await self._handle_response_schema_error(
                    resolved_request,
                    err.__cause__,
                )

            raise

        return resolved_response

    async def _handle_response_schema_error(
        self,
        request: requests.Request,
        exc: validation_exceptions.InvalidSchemaValue,
    ) -> responses.Response:
        self._response_logger.info(
            "Response body does not validate against schema",
            body=exc.value,
            source="transport",
        )

        self._logger.error(
            "Response body does not validate against schema",
            errors=[
                error.dict()
                for error in validation.invalid_schema_value_to_errors(
                    exc=exc,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            ],
        )

        return await handlers.server_error_handler(request, exc)

    async def _handle_validation_error(
        self,
        request: requests.Request,
        err: OpenAPIError,
    ) -> responses.Response:
        if isinstance(err, PathNotFound):
            return await handlers.server_error_handler(
                request,
                exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND),
            )

        match err.__cause__:
            case security_exceptions.SecurityNotFound():
                return await handlers.server_error_handler(
                    request,
                    exceptions.HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    ),
                )
            case validation_exceptions.InvalidSchemaValue():
                return await handlers.validation_error_handler(request, err.__cause__)
            case _:
                return await handlers.server_error_handler(
                    request,
                    exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST),
                )
