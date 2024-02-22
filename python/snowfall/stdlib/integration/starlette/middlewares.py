import enum
import http
from collections.abc import Awaitable, Callable, Container
from typing import cast

import sentry_sdk
from openapi_core import protocols
from starlette import (
    applications,
    background,
    requests,
    responses,
    types,
)
from starlette.middleware import base

from snowfall.stdlib.integration.starlette import handlers, messages, validation
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


class ValidationMode(enum.StrEnum):
    disabled = "disabled"
    eager = "eager"
    lazy = "lazy"


class ValidationMiddleware(base.BaseHTTPMiddleware):
    def __init__(
        self,
        app: applications.Starlette,
        validator: validation.Validator,
        *,
        excluded_status_codes: Container[int] | None = None,
        validation_mode: ValidationMode = ValidationMode.disabled,
    ):
        super().__init__(app)
        self._logger = stdout.get_logger()
        self._response_logger = stdout.get_logger()
        self._validator = validator
        self._excluded_status_codes = excluded_status_codes or []
        self._validation_mode = validation_mode

    async def dispatch(
        self,
        request: requests.Request,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
    ) -> responses.Response:
        resolved_request = await resolve_request(request)
        openapi_request = await validation.request_to_openapi(resolved_request)
        openapi_result = await self._validator.validate_request(openapi_request)
        errors = list(validation.openapi_errors_to_errors(openapi_result.errors))

        if errors:
            return await handlers.multiple4xx_error_handler(
                request=request,
                errors=errors,
            )

        resolved_request.scope["parsed_query_string"] = openapi_result.parameters.query
        resolved_request.scope["security"] = openapi_result.security

        return await self._dispatch(call_next, openapi_request, resolved_request)

    async def _dispatch(
        self,
        call_next: Callable[[requests.Request], Awaitable[responses.Response]],
        openapi_request: protocols.Request,
        resolved_request: requests.Request,
    ) -> responses.Response:
        response = await call_next(resolved_request)
        response = await resolve_response(response)

        if response.status_code in self._excluded_status_codes:
            return response

        match self._validation_mode:
            case ValidationMode.disabled:
                return response
            case ValidationMode.eager:
                return await self._validate_response(
                    openapi_request=openapi_request,
                    resolved_request=resolved_request,
                    resolved_response=response,
                )
            case ValidationMode.lazy:
                messages.add_background_task(
                    response,
                    background.BackgroundTask(
                        self._validate_response,
                        openapi_request=openapi_request,
                        resolved_request=resolved_request,
                        resolved_response=response,
                    ),
                )

                return response

    async def _validate_response(
        self,
        openapi_request: protocols.Request,
        resolved_request: requests.Request,
        resolved_response: responses.Response,
    ) -> responses.Response:
        openapi_response = await validation.response_to_openapi(resolved_response)
        openapi_result = await self._validator.validate_response(
            openapi_request,
            openapi_response,
        )
        errors = list(validation.openapi_errors_to_errors(openapi_result.errors))

        if errors:
            self._response_logger.error(
                "Response body does not validate against schema",
                body=resolved_response.body,
                errors=[error.model_dump() for error in errors],
            )

            return handlers.error_response_from_status(
                int(http.HTTPStatus.INTERNAL_SERVER_ERROR),
            )

        return resolved_response
